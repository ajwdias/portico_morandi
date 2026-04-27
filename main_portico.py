import openseespy.opensees as ops
import numpy as np
import matplotlib.pyplot as plt
import Geometry_Materials_atualizado as geom 

# 1. IDENTIFICAÇÃO (Baseado no seu print)
node_topo_left = 201
nos_base = [101, 102]

# 2. CONFIGURAÇÃO DA CARGA VERTICAL (Morandi 2018)
# No artigo, são 400kN por coluna. 
P_vertical = -400.0 

ops.timeSeries('Linear', 501)
ops.pattern('Plain', 501, 501)
ops.load(201, 0.0, P_vertical, 0.0)
ops.load(202, 0.0, P_vertical, 0.0)

# Análise Gravítica
ops.constraints('Transformation')
ops.numberer('RCM')
ops.system('BandGeneral')
ops.test('NormDispIncr', 1.0e-7, 100)
ops.algorithm('Newton')
ops.integrator('LoadControl', 0.1)
ops.analysis('Static')
ops.analyze(10)
ops.loadConst('-time', 0.0)

# 3. ANÁLISE PUSHOVER
ops.timeSeries('Linear', 601)
ops.pattern('Plain', 601, 601)
ops.load(node_topo_left, 1.0, 0.0, 0.0)

# AJUSTE DE PASSO PARA METROS:
# 0.0005 m = 0.5 mm por passo. 
# Para chegar a 60mm (0.06m), precisamos de 120 passos.
dU = 0.0005 
n_passos = 150 

ops.integrator('DisplacementControl', node_topo_left, 1, dU)
ops.analysis('Static')

curva_d, curva_v = [], []

print(f"Iniciando Pushover no nó {node_topo_left}...")

for i in range(n_passos):
    ok = ops.analyze(1)
    
    # Estratégia de Convergência se falhar
    if ok != 0:
        print(f"-> Tentativa de resgate no passo {i}...")
        ops.algorithm('NewtonLineSearch')
        ok = ops.analyze(1)
        ops.algorithm('Newton') # Volta ao normal
        
    if ok != 0:
        print(f"Corte na convergência no passo {i}. Finalizando.")
        break
    
    # Gravação de Dados
    ops.reactions()
    d = ops.nodeDisp(node_topo_left, 1) * 1000 # Convertendo para mm para o gráfico
    v = -sum(ops.nodeReaction(b, 1) for b in nos_base)
    
    curva_d.append(d)
    curva_v.append(v)
    
    if i % 20 == 0:
        print(f"Passo {i}: Deslocamento = {d:.2f} mm | Força = {v:.2f} kN")

# 4. GRÁFICO FINAL
plt.figure(figsize=(10,6))
plt.plot(curva_d, curva_v, 'b-', linewidth=2, label='Simulação OpenSees (TNT)')
plt.title('Curva de Capacidade - Pórtico Morandi (2018)')
plt.xlabel('Deslocamento Lateral (mm)')
plt.ylabel('Cortante na Base (kN)')
plt.grid(True, which='both', linestyle='--')
plt.legend()
plt.show()