import openseespy.opensees as ops
import numpy as np
import matplotlib.pyplot as plt
import Geometry_Materials_atualizado_certo as geom 

# --- 1. CONFIGURAÇÃO INICIAL E GRAVIDADE ---

# Identificação
node_topo_left = 201
nos_base = [101, 102]
P_vertical = -400.0 

# Aplicar Carga Gravítica
ops.timeSeries('Linear', 501)
ops.pattern('Plain', 501, 501)
ops.load(201, 0.0, P_vertical, 0.0)
ops.load(202, 0.0, P_vertical, 0.0)

ops.constraints('Transformation')
ops.numberer('RCM')
ops.system('BandGeneral')
ops.test('NormDispIncr', 1.0e-7, 100)
ops.algorithm('Newton')
ops.integrator('LoadControl', 0.1)
ops.analysis('Static')
ops.analyze(10)
ops.loadConst('-time', 0.0)