import openseespy.opensees as ops
import numpy as np
import opsvis as opsv
import matplotlib.pyplot as plt

exec(open('Geometry_Materials_atualizado_certo.py').read())
# ---------------------------------------------------------
# DADOS
# ---------------------------------------------------------
b_beam = 0.35
h_beam = 0.35
b_col = b_beam
h_col = h_beam
density_concrete = 2500  # kg/m³

qVigas_Pp = b_beam * h_beam * density_concrete * 9.81  # N/m

Extremos_Discretiza_Beam = 1
Internos_Discretiza_Beam = 1
Mid_discretiza_Beam = 2

# ---------------------------------------------------------
# NÓS PRINCIPAIS
# ---------------------------------------------------------
nome_nos = ops.getNodeTags()

nos_pilares = []
massa_pil = []

for no in nome_nos:
    if len(str(no)) == 3 or len(str(no)) == 4:
        nos_pilares.append(no)
        massa_pil.append([no, 0.0])

# ---------------------------------------------------------
# ELEMENTOS
# ---------------------------------------------------------
nome_elementos = ops.getEleTags()
matriz_elementos = np.zeros((len(nome_elementos), 5))

ii = 0
for eleTag in nome_elementos:
    no_i, no_j = ops.eleNodes(eleTag)

    matriz_elementos[ii, 0] = eleTag
    matriz_elementos[ii, 1] = ops.nodeCoord(no_i, 1)
    matriz_elementos[ii, 2] = ops.nodeCoord(no_i, 2)
    matriz_elementos[ii, 3] = ops.nodeCoord(no_j, 1)
    matriz_elementos[ii, 4] = ops.nodeCoord(no_j, 2)

    ii += 1   # ESSA LINHA ESTAVA FALTANDO

# ---------------------------------------------------------
# MASSA DAS VIGAS
# ---------------------------------------------------------
for info_elemento in matriz_elementos:
    eleTag = int(info_elemento[0])

    if eleTag == 0:
        continue

    elemento = str(eleTag)

    # Elementos terminados em 1 são vigas
    if elemento[-1] == '1':

        no1_vao = int(elemento[0:-4])
        no2_vao = no1_vao + 1

        if no1_vao not in nos_pilares or no2_vao not in nos_pilares:
            continue

        Vao_L = abs(ops.nodeCoord(no2_vao, 1) - ops.nodeCoord(no1_vao, 1))

        qSlabs = 0
        q_Viga = qVigas_Pp + qSlabs * Vao_L / 4

        divisor = (
            Extremos_Discretiza_Beam * 2
            + Internos_Discretiza_Beam * 2
            + Mid_discretiza_Beam
        )

        massa_por_no = round((q_Viga * Vao_L / divisor / 2) / 9.81, 2)

        indice_no_esq = nos_pilares.index(no1_vao)
        indice_no_dir = nos_pilares.index(no2_vao)

        massa_pil[indice_no_esq][1] += massa_por_no
        massa_pil[indice_no_dir][1] += massa_por_no

print("This is the mass matrix of the beams:")
print(massa_pil)

# ---------------------------------------------------------
# MASSA DOS PILARES
# ---------------------------------------------------------
maior_pavimento = 1

for pilar in nos_pilares:
    pav = int(str(pilar)[0:-2])
    maior_pavimento = max(maior_pavimento, pav)

num_pav = maior_pavimento

massPav = [0.0] * num_pav
SomaProdutoMassasX = [0.0] * num_pav
SomaProdutoMassasY = [0.0] * num_pav
nos_base = []

# Detecta alturas dos pavimentos automaticamente
Z_pavs = {}

for no in nos_pilares:
    pav = int(str(no)[0:-2])
    Z_pavs[pav] = ops.nodeCoord(no, 2)

for pilar in nos_pilares:
    pav = int(str(pilar)[0:-2])

    if pav == 1:
        nos_base.append(pilar)
        continue

    L_pilar = abs(Z_pavs[pav] - Z_pavs[pav - 1])

    Pil_mass_pp = b_col * h_col * L_pilar * density_concrete

    indice_pilar = nos_pilares.index(pilar)
    massa_pil[indice_pilar][1] += Pil_mass_pp

    massa_total = massa_pil[indice_pilar][1]

    ops.mass(pilar, massa_total, massa_total, 1e-9)

    print(pilar, "massa:", massa_total)

    massPav[pav - 1] += massa_total
    SomaProdutoMassasX[pav - 1] += massa_total * ops.nodeCoord(pilar, 1)
    SomaProdutoMassasY[pav - 1] += massa_total * ops.nodeCoord(pilar, 2)

print("This is the mass matrix, including the columns mass:")
print(massa_pil)

