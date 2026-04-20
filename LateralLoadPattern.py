#############################################################
################### LATERAL LOAD PATTERN ####################
#############################################################

import numpy as np
import openseespy.opensees as ops


# Defining the lateral load pattern

# Criando um padrão de cargas para Análise PushOver
novo_pattern = tag_pattern + 1
ops.pattern("Plain", novo_pattern, tag_timeseries)

#Obs: Inserindo o formato de cargas do Pushover:
# Opção 1: Carregamento Modo1x
# Opção 2: Carregamento Retangular
# Opção 3: Carregamento Triangular

# Opção 1: Carregamento Modo1x
# for pav in range(2,num_pav+1):
#     no_mestre = int(str(pav) + str('01'))
#     fator_carga = abs(ops.nodeEigenvector(no_mestre, Modo1x_Initial, 1))
#     # print(fator_carga)
#     ops.load(no_mestre, fator_carga, 0, 0)

# Opção 2: Carregamento Retangular
# for pav in range(2,num_pav+1):
#     no_mestre = int(str(pav) + str('01'))
#     fator_carga = 1
#     #para x
#     ops.load(no_mestre, fator_carga, 0, 0)

# Opção 3: Carregamento Triangular
# for pav in range(2,num_pav+1):
#     no_mestre = int(str(pav) + str('01'))
#     fator_carga = ops.nodeCoord(no_mestre, 2) / ops.nodeCoord(num_pav, 2)
    
#     #para x
#     ops.load(no_mestre, fator_carga, 0, 0)

# --- ANÁLISE CÍCLICA ---

#LoadControl
force = [0, 
         -40, 40, -40, 40, -40, 40, 
         -80, 80, -80, 80, -80, 80]

passo_force = 1 #kN
for force_alvo in force:
   
    force_atual = ops.getTime()
  
    deltaF = force_alvo - force_atual
    
    num_steps = int(abs(deltaF) / passo_force)
    dF_increment = deltaF/num_steps    

    tag_timeseries_force = 22
    ops.timeSeries('Linear', tag_timeseries_force)
    ops.pattern('Plain', novo_pattern, tag_timeseries_force)

    ops.analysis('Static')
    ops.algorithm('NewtonLineSearch') 
    ops.test('NormUnbalance', 1e-05, 10, 0) 

    ops.integrator('LoadControl', dF_increment)
    ops.analysis('Static')
    
    for i in range(num_steps):
        ok = ops.analyze(1)

P_lateral = 1
ops.load(node_topo, P_lateral, 0.0, 0.0) 
dof_lateral = 1    

disp_picos = [-10.94, 10.94, -10.94, 10.94, -10.94, 10.94, 
            -12.50, 12.50, -12.50, 12.50, -12.50, 12.50,
            -15.63, 15.63, -15.63, 15.63, -15.63, 15.63,
            -18.75, 18.75, -18.75, 18.75, -18.75, 18.75, 
            -25.00, 25.00, -25.00, 25.00, -25.00, 25.00,
            -31.25, 31.25, -31.25, 31.25, -31.25, 31.25,
            -39.06, 39.06, -39.06, 39.06, -39.06, 39.06,
            -46.88, 46.88, -46.88, 46.88, -46.88, 46.88,
            -54.69, 54.69, -54.69, 54.69, -54.69, 54.69,
            -62.50, 62.50, -62.50, 62.50, -62.50, 62.50,
            -78.13, 78.13, -78.13, 78.13, -78.13, 78.13,
            -93.75, 93.75, -93.75, 93.75, -93.75, 93.75,
            -109.38, 109.38, -109.38, 109.38, -109.38, 109.38]*1e-3


dD = 0.00005 # incremento de deslocamento (0.05 mm)

# DisplacementControl
for i in range(len(disp_picos)):
    D_inicio = disp_picos[i]
    D_fim = disp_picos[i+1]
    dDelta = D_fim - D_inicio
   
    nSteps = int(abs(dDelta) / dD) 
    if nSteps == 0: nSteps = 1

    tag_timeseries_disp = 33
    ops.timeSeries('Linear', tag_timeseries_disp)
    ops.pattern('Plain', novo_pattern, tag_timeseries_disp)

    ops.analysis('Static')
    ops.algorithm('NewtonLineSearch') 
    ops.test('NormUnbalance', 1e-05, 10, 0) 
        
    dU_increment = dDelta / nSteps
    ops.integrator('DisplacementControl', node_topo, dof_lateral, dU_increment)
    
    print(f"Segmento {i+1}: {D_inicio:.4f} m -> {D_fim:.4f} m em {nSteps} passos.")
    
    ok = ops.analyze(nSteps) 