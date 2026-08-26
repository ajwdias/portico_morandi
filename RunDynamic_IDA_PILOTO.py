"""
RunDynamic_IDA_PILOTO_CORRIGIDO.py

Coloque este arquivo na MESMA pasta de:
    RunDynamic_IDA_Fragilidade.py

Ele cria uma execução piloto sem alterar o arquivo principal:
2 terremotos x 10 escalas = 20 análises.
"""

from pathlib import Path
import re

base_dir = Path(__file__).resolve().parent
arquivo_base = base_dir / "RunDynamic_IDA_Fragilidade.py"

if not arquivo_base.exists():
    raise FileNotFoundError(
        "Nao encontrei RunDynamic_IDA_Fragilidade.py na mesma pasta deste arquivo."
    )

source = arquivo_base.read_text(encoding="utf-8")

sismos_piloto = [
    "RSN4876_CHUETSU_65059EW.AT2",
    "RSN4876_CHUETSU_65059NS.AT2",
]
fatores_piloto = [1, 2, 4, 6, 8, 12, 16, 24, 32, 40]

# 1) Apenas dois sismos
novo_filtro = "filtro_terremotos = " + repr(sismos_piloto) + "  # PILOTO"

source, n = re.subn(
    r"(?m)^filtro_terremotos\s*=\s*None[^\n]*$",
    novo_filtro,
    source,
    count=1,
)

if n == 0:
    source, n = re.subn(
        r"(?m)^filtro_terremotos\s*=\s*\[[^\n]*\][^\n]*$",
        novo_filtro,
        source,
        count=1,
    )

if n == 0:
    raise RuntimeError("Nao encontrei a variavel filtro_terremotos no arquivo principal.")

# 2) Dez fatores de escala
nova_escala = "fatores_escala = " + repr(fatores_piloto) + "  # PILOTO"

source, n = re.subn(
    r"(?m)^fatores_escala\s*=\s*\[[^\n]*\][^\n]*$",
    nova_escala,
    source,
    count=1,
)

if n == 0:
    raise RuntimeError("Nao encontrei a variavel fatores_escala no arquivo principal.")

# 3) Nao gerar figuras durante o piloto
source = re.sub(
    r"(?m)^salvar_figuras\s*=\s*True[^\n]*$",
    "salvar_figuras = False  # PILOTO",
    source,
    count=1,
)

# 4) Silenciar as mensagens CTestNormDispIncr quando o printFlag for 2
source = source.replace(
    "ops.test('NormDispIncr', tolerancia, max_iter, 2)",
    "ops.test('NormDispIncr', tolerancia, max_iter, 0)"
)
source = source.replace(
    'ops.test("NormDispIncr", tolerancia, max_iter, 2)',
    'ops.test("NormDispIncr", tolerancia, max_iter, 0)'
)

# 5) Resultados do piloto em pasta separada
source = source.replace(
    "ida_root = f'./Results_Dynamic_Multisismos/{frame_base}/IDA'",
    "ida_root = f'./Results_Dynamic_Multisismos/{frame_base}/IDA_PILOTO'"
)
source = source.replace(
    "frame_folder = f'{frame_base}/IDA/SF_{esc:g}'",
    "frame_folder = f'{frame_base}/IDA_PILOTO/SF_{esc:g}'"
)

print("=" * 72)
print("TESTE PILOTO DA IDA")
print("2 terremotos x 10 fatores de escala = 20 analises")
print("Sismos:")
for s in sismos_piloto:
    print(" -", s)
print("Escalas:", fatores_piloto)
print("=" * 72)

namespace = {
    "__name__": "__main__",
    "__file__": str(arquivo_base),
}

exec(compile(source, str(arquivo_base), "exec"), namespace)