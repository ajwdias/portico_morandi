"""
Ajuste_Curvas_Fragilidade.py
============================
Lê o arquivo FRAGILITY_DATABASE.csv produzido por RunDynamic_IDA_Fragilidade.py
 e ajusta curvas de fragilidade lognormais por máxima verossimilhança.

Modelo:
    P[DS >= ds | IM] = Phi((ln(IM) - ln(theta)) / beta)

IM padrão: Sa(T1) [g]
EDP: IDR máximo [%]
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.stats import norm

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO
# -----------------------------------------------------------------------------
frame_base = 'BareFrame'
base_dir = os.path.join('Results_Dynamic_Multisismos', frame_base, 'IDA')
arquivo_entrada = os.path.join(base_dir, 'FRAGILITY_DATABASE.csv')
im_col = 'Sa(T1) (g)'
edp_col = 'Max. IDR (%)'

estados = {
    'DS1_Slight': 0.4,
    'DS2_Moderate': 0.6,
    'DS3_Extensive': 1.6,
    'DS4_Complete': 4.0,
}

# -----------------------------------------------------------------------------
# FUNÇÕES
# -----------------------------------------------------------------------------
def nll_lognormal(params, im, y):
    """Negative log-likelihood para observações binárias de excedência."""
    ln_theta, ln_beta = params
    theta = np.exp(ln_theta)
    beta = np.exp(ln_beta)
    z = (np.log(im) - np.log(theta)) / beta
    p = norm.cdf(z)
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return -np.sum(y * np.log(p) + (1 - y) * np.log(1 - p))


def ajustar_fragilidade(im, y):
    im = np.asarray(im, dtype=float)
    y = np.asarray(y, dtype=int)
    mask = np.isfinite(im) & (im > 0) & np.isfinite(y)
    im = im[mask]
    y = y[mask]

    if len(im) < 4:
        return None, 'Poucos dados válidos.'
    if len(np.unique(y)) < 2:
        return None, 'Não há simultaneamente excedências e não excedências.'

    # Chute inicial: mediana das IMs próximas da transição e beta moderado.
    theta0 = np.median(im)
    beta0 = 0.5
    res = minimize(
        nll_lognormal,
        x0=[np.log(theta0), np.log(beta0)],
        args=(im, y),
        method='Nelder-Mead',
        options={'maxiter': 20000, 'xatol': 1e-10, 'fatol': 1e-10},
    )
    if not res.success:
        return None, f'Falha no ajuste: {res.message}'

    theta = float(np.exp(res.x[0]))
    beta = float(np.exp(res.x[1]))
    return {'theta_g': theta, 'beta': beta, 'n': len(im), 'n_exc': int(y.sum())}, 'OK'


# -----------------------------------------------------------------------------
# LEITURA E LIMPEZA
# -----------------------------------------------------------------------------
if not os.path.isfile(arquivo_entrada):
    raise FileNotFoundError(
        f'Arquivo não encontrado: {arquivo_entrada}\n'
        'Rode primeiro RunDynamic_IDA_Fragilidade.py.'
    )

df = pd.read_csv(arquivo_entrada)

# Apenas análises concluídas entram no ajuste; falha numérica não vira IDR = 0.
df_ok = df[df['Analysis'].eq('SUCESSO')].copy()
df_ok[im_col] = pd.to_numeric(df_ok[im_col], errors='coerce')
df_ok[edp_col] = pd.to_numeric(df_ok[edp_col], errors='coerce')
df_ok = df_ok[np.isfinite(df_ok[im_col]) & np.isfinite(df_ok[edp_col]) & (df_ok[im_col] > 0)]

os.makedirs(base_dir, exist_ok=True)

# -----------------------------------------------------------------------------
# FIGURA IDA: Sa(T1) x IDR, uma curva por registro
# -----------------------------------------------------------------------------
plt.figure(figsize=(8, 6))
for eq, g in df_ok.groupby('Earthquake'):
    g = g.sort_values(im_col)
    plt.plot(g[edp_col], g[im_col], marker='o', linewidth=1, markersize=3, alpha=0.65)
for nome_ds, lim in estados.items():
    plt.axvline(lim, linestyle='--', linewidth=1, label=f'{nome_ds}: {lim:.2f}%')
plt.xlabel('IDR máximo (%)')
plt.ylabel('Sa(T1) (g)')
plt.title('Curvas IDA — Sa(T1) × IDR máximo')
plt.grid(True, alpha=0.3)
plt.legend(fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(base_dir, 'IDA_SaT1_vs_IDR.png'), dpi=300)
plt.close()

# -----------------------------------------------------------------------------
# AJUSTE DAS CURVAS
# -----------------------------------------------------------------------------
parametros = []
curvas = []

im_min = max(df_ok[im_col].min() * 0.8, 1e-4)
im_max = df_ok[im_col].max() * 1.2
im_grid = np.logspace(np.log10(im_min), np.log10(im_max), 300)

plt.figure(figsize=(8, 6))

for ds, limite_idr in estados.items():
    y = (df_ok[edp_col].to_numpy() >= limite_idr).astype(int)
    ajuste, status = ajustar_fragilidade(df_ok[im_col].to_numpy(), y)

    linha = {
        'Damage State': ds,
        'IDR Limit (%)': limite_idr,
        'Status': status,
        'Theta Sa(T1) (g)': np.nan,
        'Beta': np.nan,
        'N': len(y),
        'N Exceedances': int(y.sum()),
    }

    if ajuste is not None:
        theta = ajuste['theta_g']
        beta = ajuste['beta']
        linha.update({
            'Theta Sa(T1) (g)': theta,
            'Beta': beta,
            'N': ajuste['n'],
            'N Exceedances': ajuste['n_exc'],
        })

        prob = norm.cdf((np.log(im_grid) - np.log(theta)) / beta)
        plt.plot(im_grid, prob, linewidth=2, label=f'{ds} (θ={theta:.3f}g, β={beta:.3f})')
        curvas.append(pd.DataFrame({
            'Damage State': ds,
            'Sa(T1) (g)': im_grid,
            'Probability of Exceedance': prob,
        }))
    else:
        print(f'{ds}: curva não ajustada — {status}')

    parametros.append(linha)

param_df = pd.DataFrame(parametros)
param_df.to_csv(os.path.join(base_dir, 'FRAGILITY_PARAMETERS.csv'), index=False)

if curvas:
    pd.concat(curvas, ignore_index=True).to_csv(
        os.path.join(base_dir, 'FRAGILITY_CURVES.csv'), index=False)

plt.xlabel('Sa(T1) (g)')
plt.ylabel('Probabilidade de excedência')
plt.ylim(0, 1.02)
plt.xlim(left=0)
plt.title('Curvas de Fragilidade')
plt.grid(True, alpha=0.3)
plt.legend(fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(base_dir, 'CURVAS_FRAGILIDADE.png'), dpi=300)
plt.close()

# -----------------------------------------------------------------------------
# RESUMO DE CONTROLE
# -----------------------------------------------------------------------------
controle = []
for ds, limite in estados.items():
    exc = int((df_ok[edp_col] >= limite).sum())
    controle.append({
        'Damage State': ds,
        'IDR Limit (%)': limite,
        'Successful Analyses': len(df_ok),
        'Exceedances': exc,
        'Non-exceedances': len(df_ok) - exc,
    })
pd.DataFrame(controle).to_csv(os.path.join(base_dir, 'FRAGILITY_DATA_CHECK.csv'), index=False)

print('\nAjuste concluído.')
print(param_df.to_string(index=False))
print(f'\nArquivos salvos em: {os.path.abspath(base_dir)}')
