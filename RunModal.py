import openseespy.opensees as ops
import opsvis as opsv
import numpy as np
import os


base_dir = os.path.dirname(__file__)


def analise_modal(numero_de_modos = 5, eps_amortecimento = 0.05):
# =============================================================================
#                              Análise Modal
# =============================================================================
    ops.wipeAnalysis()
    # Calculando modos de vibração e matriz de amortecimento
    numEigen = numero_de_modos #Número de eigenvalores desejados
    eigenValues = ops.eigen('-genBandArpack',numEigen)  
    # # #'-genBandArpack' encontra n-1 modos (mais rapido)
    # # #'-fullGenLapack' encontra n modos (mais demorado)
    w1 = np.sqrt(eigenValues[0])
    w2 = np.sqrt(eigenValues[1])
    w3 = np.sqrt(eigenValues[2])
    T1_static = 2*np.pi/w1
    T2_static = 2*np.pi/w2
    T3_static = 2*np.pi/w3
    alphaM = (1)*eps_amortecimento*(2*w1*w3)/(w1*w3)
    betaKcurr = (0)*2*eps_amortecimento/(w1+w3)
    betaKcomm = (1)*2*eps_amortecimento/(w1+w3)
    betaKinit = (0)*2*eps_amortecimento/(w1+w3)
    ops.rayleigh(alphaM, betaKcurr, betaKinit, betaKcomm) #Rayleigh Damping (Matriz C)
    
    # compute the modal properties
    Propriedades_Modal = ops.modalProperties("-print", "-file", "ModalReport.txt", "-unorm", "-return")    
    
    opsv.plot_mode_shape(1, 100, node_supports=False, endDispFlag=0)
    print('Período de vibração do 1o modo:', T1_static)
    opsv.plot_mode_shape(2, 100, node_supports=False, endDispFlag=0)
    print('Período de vibração do 2o modo:', T2_static)
    opsv.plot_mode_shape(3, 100, node_supports=False, endDispFlag=0)
    print('Período de vibração do 3o modo:', T3_static)
    return Propriedades_Modal, T1_static


ops.wipeAnalysis() #Elimina todo analisis previo, sirva para hacer barrido de frecuencias tb
# ops.wipe()  # Cuabdi activo este, el RunPushdown del RunLHS no está rodando, da error: On entry to DGBSV parameter number 9 had an illegal value
#Definir Modelo
# ops.model('basic','-ndm',2)

Infill_wall = 'No' # Yes or No
offset = 'No' # Yes or No

# exec(open('Geometry_Materials.py').read())
import os
base_dir = os.path.dirname(__file__)
exec(open(os.path.join(base_dir, 'Geometry_Materials_atualizado.py')).read(), globals())

# exec(open('Geometry.py').read())

import os
base_dir = os.path.dirname(__file__)

exec(open(os.path.join(base_dir, 'VerticalLoad.py')).read(), globals())


# exec(open('VerticalLoad.py').read())

# Mass definition
import os
base_dir = os.path.dirname(__file__)

exec(open(os.path.join(base_dir, 'Mass.py')).read(), globals())


# exec(open('Mass.py').read())
print("The mass has been defined")

# -----------------------------------------------------------
# Aplicar carga vertical e travar o estado inicial (igual ao ensaio TNT)
# -----------------------------------------------------------

ops.constraints('Transformation')
ops.numberer('RCM')
ops.system('BandGeneral')
ops.test('NormDispIncr', 1.0e-12, 10, 3)
ops.algorithm('Newton')
ops.integrator('LoadControl', 1)
ops.analysis('Static')

ops.analyze(1)

# Mantém a carga aplicada (ativa a rigidez geométrica P-Delta)
ops.loadConst('-time', 0.0)


# ops.wipeAnalysis()


# # Aplico la carga vertical

# # 1. ConstraintsHandler
# ops.constraints('Transformation')   

# print('Aplicado constraints Transformation')

# # 2. DOF_Numberer
# ops.numberer('RCM')

# # 3. SystemOfEqn/Solver
# ops.system('BandGeneral')

# # 4. Convergence Test

# ops.test('NormDispIncr', 1.0e-12, 10, 3)   # 1.0e-12

# # 5. SolutionAlgorithm
# ops.algorithm('Newton')

# # 6. Integrador
# ops.integrator('LoadControl', 1)

# # 7. Analysis
# ops.analysis('Static')

# print('Aplicado Static Analysis')


# # 8. Analyze
# ops.analyze(1) #1/IncrCarga  número de pasos a analizar

# print('Carga Vertical Aplicada')
# # Obtener la matriz de Rigidez 

# ops.loadConst('-time',0.0) # Mantener la carga aplicada (constante).
# #Si no coloco esa l[inea al hacer otro an[alisis se aplica el doble de carga
# #en este punto la rigidez ya no es la inicial, es la inicial-rigidez geométrica.4

numEigen = 3
Propriedades_Modal, T1_static = analise_modal(numero_de_modos = numEigen)
# opsv.plot_mode_shape(1, 100, node_supports=False, endDispFlag=0)
# opsv.plot_mode_shape(2, 100, node_supports=False, endDispFlag=0)
# opsv.plot_mode_shape(3, 100, node_supports=False, endDispFlag=0)

# Obtendo qual modo de vibração é Flexional X
Modo1x = 1 + Propriedades_Modal['partiMassRatiosMX'].index(max(Propriedades_Modal['partiMassRatiosMX']))
T1x = Propriedades_Modal['eigenPeriod'][Modo1x - 1]