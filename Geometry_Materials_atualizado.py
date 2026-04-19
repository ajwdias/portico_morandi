import openseespy.opensees as ops
import matplotlib.pyplot as plt
import numpy as np
import opsvis as opsv
import math as math
from datetime import datetime


# =============================================================================
#                        Definição das Prop. dos Materiais                     
# =============================================================================

# Variáveis aleatórias
# fc  => resistencia do concreto à compressão            media = 33,01  MPa   desvio = 4,87   normal
# fy  => resistência do aço ao escoamento (longitudinal) media = 576,0  MPa   desvio = 46,08  normal
# fyw => resistência do aço ao escoamento (transversal)  media = 690,93 MPa   desvio = 55,27  normal
# Es  => módulo de elasticidade do aço                   media = 201    GPa   desvio = 6,63   normal
# eps => taxa de amortecimento estrutural                media = 0,042        desvio = 0,032  lognormal

# fc_normal = 38.6 # 38.6 Valor convergiendo = 37.81.Primer piso es de 41.3MPa y el segundo de 31.8MPa. La media es de 36.55 
# Colocando altas resistencias do concreto por ejemplo 60MPa no muda mucho la parte no lineal.

# Nodo 203 con ruptura barra = 38.6 para ruptura de 0.18 de la barra  # 8 elements
# Nodo 203 sin ruptura barra = 38.3 para ruptura de 0.18 de la barra  # 8 elements


# =============================================================================
#      Definindo TAG dos Materiais
# =============================================================================

# Aco_Tag = 2 
  
# DiagonalAlvenaria_Tag_off = 2000 
#########################################################################################################################
################################################## FIBER COLUMNS ########################################################
#########################################################################################################################

def sec_fibrasconfinadas(SectionTag = 3, IntegraTag = 3, ConcretoC_Tag = 4, ConcretoNC_Tag = 5, Steel_Tag = [1, 2],MinMaxSteel_Tag = [1,2] , numIntgrPts=3, 
                b_beam = 0.20, h_beam=0.40, fc = 0, cobrimento = 0.04, 
                diam_longitudinal = [0.008, 0.010,0.008,0.008], fy_ = [500,500] , Es_ =  200,
                    barras_camadas = [2, 2,2,2], PosIniCam = [2, -2,1,-1], PosFinalCam = [2, -2,1,-1],
                    diam_transversal = 0.005, espacamento_s = 0.10, npernas_xx = 2 , npernas_yy = 2, fy_transv = 600, MinStrain_Steel = [-0.17, -0.17], MaxStrain_Steel = [0.17, 0.17],b_steel = [0.0024,  0.0024],
                    NumDivCore_z = 1, NumDivCore_y = 9, NumDivInf_z = 1, NumDivInf_y = 2, NumDivSup_z = 1, NumDivSup_y = 2, NumDivDir_z = 1, NumDivDir_y = 16, NumDivEsq_z = 1, NumDivEsq_y = 16
                        ):
    
    ##########################
    # Concreto Não Confinado - CONCRETE01
    ##########################

    ConcretoNC_Tag_value = ConcretoNC_Tag
    fc_inicial = (fc)*(10**6)            #resistência a compressao aos 28dias (negativo)
    Ec = 8200*fc**(3/8)*(10**6) #N/m²            #Modulo de elasticidade
    epsc = 2*fc_inicial/Ec             #Deformação máxima do concreto
    fpc_u_NC = 0.2*fc_inicial             #tensão na ruptura
    epsc_u_NC = 5*epsc # 0.009       # estava 0.009 e5*epsc deformação na ruptura

    # try:
    #     # ops.uniaxialMaterial('Concrete01', matTag, fpc, epsc0, fpcu, epsU)
    #     ops.uniaxialMaterial('Concrete01', ConcretoNC_Tag_value, -fc_inicial, -epsc, -fpc_u_NC, -epsc_u_NC)
    # except:
    #     print('Tudo bem. Significa que o Concreto Não Confinado (Tag = 1) já foi adicionado anteriormente no modelo.')
    # pass

    #####################################
    # Concreto Não Confinado - CONCRETE02
    #####################################

    # Los parámetros de la parte a compresión fueron definidos en el Concrete01

    lambda_c = 0.1               #razao entre a inclinacao de descarga epsc_u e a inclinacao inicial epsc0
    ftc_NC = 0.6228*np.sqrt(fc)*(10**6) #N/m² Tração        #PAPER34
    Ec_tracao_NC = ftc_NC/0.002        #Modulo Elasticidade a Tração

    try:
        ops.uniaxialMaterial('Concrete02', ConcretoNC_Tag, -fc_inicial, -epsc, -fpc_u_NC, -epsc_u_NC, lambda_c, ftc_NC, Ec_tracao_NC)
    except:
        print('Tudo bem. Significa que o Concreto Não Confinado (Tag = 1) já foi adicionado anteriormente no modelo.')
    pass

    #####################################
    # Concreto Não Confinado - CONCRETE07
    #####################################

    # este no dejó colocar que el hormigón falla hasta 0.006 y pérdida de resistencia del 20%. Quise usar el minMax Material pero Fiber Section no me dejó usar

    # ConcretoNC_Tag_value = ConcretoNC_Tag
    # fc_inicial = (fc) *(10**6)            #resistência a compressao aos 28dias (negativo)
    # epsc = (fc*145.038)**(1/4)/4000       # deformacao da resistência máxima a compessão do concreto.;. Ver fórmulas de opensees.. Fc en MPa 
    # Ec = 8200*fc**(3/8) * (10**6) #N/m²            #Modulo de elasticidade
    # ft = 0.62*np.sqrt(fc) * (10**6)
    # et = 2*ft/Ec                
    # xp = 2                      
    # xn = 2.3                    
    # r = fc/5.2 - 1.9     
    
    # try:
    #     ops.uniaxialMaterial('Concrete07', ConcretoNC_Tag, -fc_inicial, -epsc, Ec, ft, et, xp, xn, r)
    # except:
    #     print('Tudo bem. Significa que o Concreto Não Confinado (Tag = 1) já foi adicionado anteriormente no modelo.')
    #     pass
    

    ###########################################
    # MinMax Material - For Unconfined Concrete
    ###########################################

    # Encontré ruptura con 0.018 
    # minStrain_UC = -1e16 #-0.006 -1e16 para no considerar la fractura de barras de acero
    # maxStrain_UC = 1e16 # 1e16 para no considerar la fractura de barras de acero

    # ops. uniaxialMaterial('MinMax', MinMaxTag_UC , ConcretoNC_Tag, '-min', minStrain_UC, '-max', maxStrain_UC)
    
    ##############################
    # MinMax Material - For Confined Concrete
    ##############################

    # Encontré ruptura con 0.018 
    # minStrain_CC = -1e16 #-0.008 -1e16 para no considerar la ruptura del concreto
    # maxStrain_CC = 1e16 #0.003 1e16 para no considerar la ruptura del concreto

  
    ##########################
    # Steel 02
    ##########################

    for i in range(0,len(Steel_Tag)):

        # Modelo do Aço
        fy = fy_[i] * (10**6)                #tensão de escoamento do aço
        E_aco = Es_ * (10**9)             #modulo de elasticidade do aço
        b_aco = b_steel[i]
        R0 = 20                           #Valor entre 10 e 20
        cR1 = 0.9                         #cR1 = 0.925 
        cR2 = 0.08                        #Valor recomendado cR2 = 0.15
        a1 = 0.039
        a2 = 1.0
        a3 = 0.029
        a4 = 1
        
        try:
            
            print("Steel02 Steel_Tag[i]:", Steel_Tag[i], "fy:", fy, "E_aco:", E_aco, "b_aco:", b_aco, "R0:", R0, "cR1:", cR1, "cR2:", cR2, "a1:", a1, "a2:", a2, "a3:", a3, "a4:", a4)
            ops.uniaxialMaterial('Steel02', Steel_Tag[i], fy, E_aco, b_aco, R0, cR1, cR2, a1, a2, a3, a4, 0.0)
            print('Definido MinMax para o Aço')
        except:
            print('Tudo bem. Significa que o Aço (Tag = 2) já foi adicionado anteriormente no modelo.')
            pass
        # Valores acima obtidos de Carreño et al. 2020: "Material Model Parameters for the Giuffrè-Menegotto-Pinto Unixial Steel Stress-Strain Model"

        ##############################
        # MinMax Material - For Steel
        ##############################
 
        MinStrain = MinStrain_Steel[i]
        MaxStrain = MaxStrain_Steel[i]

        try:
            print([MinMaxSteel_Tag[i], Steel_Tag[i], '-min', MinStrain, '-max', MaxStrain])
            ops.uniaxialMaterial('MinMax', MinMaxSteel_Tag[i], Steel_Tag[i], '-min', MinStrain, '-max', MaxStrain)
        except:
            print(f'MinMax material para o aço (Tag = {MinMaxSteel_Tag[i]}) já foi adicionado anteriormente no modelo.')
            pass
    



    # ##########################
    # # Steel 01
    # ##########################

    # for i in range(0,len(Steel_Tag)):

    #     fy = fy_[i] * (10**6)                #tensão de escoamento do aço
    #     print("Este es el valor de fy:", fy)
    #     E_aco = Es_ * (10**9)             #modulo de elasticidade do aço
        
    #     b_aco = b_steel[i]  #  0.00030     #estaba con 0.0049 -  0.0022   -0.00477 (0.0031) Com parede   (0.0030 Sem parede: 2 elementos extremos da rótula, 8 elementos en el centro de la viga, 3 elementos base del pilar)   
    #     a1 = 0.0   #0.0           0.5   (5   20   100 estos valores da parecido aunque difeiren bastante de 0.05)
    #     a2 = 1.0      #1.0       1.0  5  20  100: dieron los mismos resultados)
    #     a3 = 0.0    #0.0     0.006       (0.01: varia pero no tanto:  0.08, 0.5, 5 varia demasiado la curva )
    #     a4 = 0.1   #1.0         (0.5, 5 , 100: no varia )

    #     # a1 =    # 0.039
    #     # a2 = 10
    #     # a3 = 10
    #     # a4 = 10

    #     try:
    #         print("Steel01 Steel_Tag[i]:", Steel_Tag[i], "fy:", fy, "E_aco:", E_aco, "b_aco:", b_aco, "a1:", a1, "a2:", a2, "a3:", a3, "a4:", a4)
    #         # uniaxialMaterial('Steel01', matTag, Fy, E0, b, a1, a2, a3, a4)
    #         ops.uniaxialMaterial('Steel01', Steel_Tag[i], fy, E_aco, b_aco, a1, a2, a3, a4)
    #     except:
    #         print('Tudo bem. Significa que o Aço (Tag = 2) já foi adicionado anteriormente no modelo.')
    #         pass

    #     ##############################
    #     # MinMax Material - For Steel
    #     ##############################
 
    #     MinStrain = MinStrain_Steel[i]
    #     MaxStrain = MaxStrain_Steel[i]

    #     try:
    #         print([MinMaxSteel_Tag[i], Steel_Tag[i], '-min', MinStrain, '-max', MaxStrain])
    #         ops.uniaxialMaterial('MinMax', MinMaxSteel_Tag[i], Steel_Tag[i], '-min', MinStrain, '-max', MaxStrain)
    #     except:
    #         print(f'MinMax material para o aço (Tag = {MinMaxSteel_Tag[i]}) já foi adicionado anteriormente no modelo.')
    #         pass





    ##########################################################################################

    # Calculation of Unconfined Concrete Strength and Strain

    area_longitudinal = [diametro**2 * math.pi / 4 for diametro in diam_longitudinal]
    area_total_separada = [n_barras_i * area_i for n_barras_i, area_i in zip(barras_camadas, area_longitudinal)]
    Ast = sum(area_total_separada)
    # area_longitudinal = 3.1415/4*self.diam_longitudinal**2
    # n_barras = sum(self.barras_camadas)
    # Ast = n_barras * area_longitudinal
    
    n_camadas = len(barras_camadas)
      
    dlinha = cobrimento + diam_transversal + min(diam_longitudinal)/2
    # dlinha = self.cobrimento + self.diam_transversal + self.diam_longitudinal/2
    slinha = espacamento_s - diam_transversal
    
    hx = b_beam - 2*cobrimento - diam_transversal   # dc
    hy = h_beam - 2*cobrimento - diam_transversal   # bc
    
    wlinha_x = ((hx - diam_transversal - 2*min(diam_longitudinal))-(npernas_yy-2)*min(diam_longitudinal)) / (npernas_yy-1)
    wlinha_y = ((hy - diam_transversal - 2*min(diam_longitudinal))-(npernas_xx-2)*min(diam_longitudinal)) / (npernas_xx-1)

    num_wlinha_x = 2 * (npernas_yy - 1)  
    num_wlinha_y = 2 * (npernas_xx - 1) 
    
    rho_cc = Ast/(hx * hy)  # ratio of area of longitudinal reinforcement to area of core of section 
    Ae = (hx * hy - num_wlinha_x*(wlinha_x**2)/6 - num_wlinha_y*(wlinha_y**2)/6)*(1-0.5*slinha/hx)*(1-0.5*slinha/hy)   # Area of effectively confined concrete core
    Acc = (hx * hy) * (1 - rho_cc) # Area of core concrete without longitudinal reinforcement (le resta área al núcle de concreto confinado hx*hy ó dc*bc)
    ke = Ae / Acc    # Coefinement effectiveness coefficient
    
    rho_x = (npernas_xx * math.pi * diam_transversal**2 / 4) / (espacamento_s*hy)   # Total area of transverse reinforcement parallel to the x axis
    rho_y = (npernas_yy * math.pi * diam_transversal**2 / 4) / (espacamento_s*hx)   # Total area of transverse reinforcement parallel to the y axis
    
    flx = ke * rho_x * fy_transv * (10**6) # Lateral confining stress on the concrete in the direction x
    fly = ke * rho_y * fy_transv * (10**6) # Lateral confining stress on the concrete in the direction y
    q = np.minimum(flx,fly)/np.maximum(flx,fly) 
    
    A = 6.8886 - (0.6069 + 17.275*q)*np.exp(-4.989*q)
    B = ((4.5)/(5/A*(0.9849-0.6306*np.exp(-3.8939*q))-0.1))-5
    xlinha = (flx + fly) / (2*(fc_inicial))
    k1 = A*(0.1+0.9/(1+B*xlinha))
    k2 = 5*k1  # para resistencia normal da armadura transversal (5k1)
    # k2 = 3*k1  # para elevada resistencia da armadura transversal (3k1)
    fator_fc_confinado = 1+k1*xlinha
    fator_ec_confinado = 1+k2*xlinha
    fc_confinado = fc_inicial*fator_fc_confinado          #Resistência máxima do concreto confinado à compressão
    ec_confinado = epsc*fator_ec_confinado         #Deformação de pico do concreto confinado à compressão 
    if fc_confinado > fc_inicial:
        xn = 30                                                      #ok
        n = Ec*ec_confinado/(fc_confinado)                           #ok
        r = n/(n-1)                                                  #ok
    else:
        fc_confinado = fc_inicial
        ec_confinado = epsc
        xn = 2.3
    
    # Aquí se define el material CONCRETO CONFINADO

    #######################################
    # Concrete01 para el hormigón confinado
    #######################################

    epsc_u_NC2 = 5*ec_confinado  #0.008 La defomración unitaria de ruptura del hormigón CONFINADO no es dado en el paper 34. Se asume 0.008. 

    # ops.uniaxialMaterial('Concrete01', matTag, fpc, epsc0, fpcu, epsU)
    # ops.uniaxialMaterial('Concrete01', ConcretoC_Tag, -fc_confinado, -ec_confinado, -fc_confinado*0.20, -epsc_u_NC2)  

    # ftc_NC = 0.6228*np.sqrt(fc_confinado)*(10**6)

    # ops.uniaxialMaterial('Concrete02', ConcretoC_Tag, -fc_confinado, -ec_confinado, -fc_confinado*0.20,  -epsc_u_NC2, lambda_c, ftc_NC, Ec_tracao_NC) 
    # print('ops.uniaxialMaterial("Concrete01",', ConcretoC_Tag,', ', -fc_confinado,', ', -ec_confinado,', ', -fpc_u_NC,', ', -epsc_u_NC2)


    #######################################
    # Concrete02 para el hormigón confinado
    #######################################

    ops.uniaxialMaterial('Concrete02', ConcretoC_Tag, -fc_confinado, -ec_confinado, -fc_confinado*0.20, -epsc_u_NC2, lambda_c, ftc_NC, Ec_tracao_NC)  
    print('ops.uniaxialMaterial("Concrete02",', ConcretoC_Tag,', ', -fc_confinado,', ', -ec_confinado,', ', -fpc_u_NC,', ', -epsc_u_NC2,', ', lambda_c,', ', ftc_NC,', ', Ec_tracao_NC)


    #######################################
    # Concrete07 para el hormigón confinado
    #######################################
    
    # ops.uniaxialMaterial('Concrete07', ConcretoC_Tag, -fc_confinado, -ec_confinado, Ec, ft, et, xp, xn, r)  
    # print('ops.uniaxialMaterial("Concrete07",', ConcretoC_Tag,', ', -fc_confinado,', ', -ec_confinado,', ', Ec,', ', ft,', ', et,', ', xp,', ', xn,', ', r)

    # ops. uniaxialMaterial('MinMax', MinMaxTag_CC , ConcretoC_Tag, '-min', minStrain_CC, '-max', maxStrain_CC)

    # Criando as Fibras da Seção
    Area = b_beam*h_beam
    Iz = b_beam*h_beam**3/12
    Iy = h_beam*b_beam**3/12
    J = Iz + Iy  
    Gc = Ec/(2*(1+0.2))
    GJ = Gc * J
    c = cobrimento   
    h = h_beam
    b = b_beam
    

    # NumDivCore_z = 1  
    # NumDivCore_y = int(np.floor((h-2*c)/c))
    # NumDivInf_z = 1
    # NumDivInf_y = 2   #2
    # NumDivSup_z = 1
    # NumDivSup_y = 2   #2
    # NumDivDir_z = 1
    # NumDivDir_y = 16   #16
    # NumDivEsq_z = 1
    # NumDivEsq_y = 16   #16
    

    
    print('vALOR DE GJ:',GJ)


    print("ConcretoC_Tag recibido =", ConcretoC_Tag)
    print("ConcretoNC_Tag recibido =", ConcretoNC_Tag)
    print("MinMaxSteel_Tag recibido =", MinMaxSteel_Tag)



    fib_sec_1 = [['section', 'Fiber', SectionTag, '-GJ', GJ],
            #    ['patch', 'quad', MinMaxTag_CC , NumDivCore_y, NumDivCore_z, -h/2+c, -b/2+c, h/2-c, -b/2+c, h/2-c, b/2-c, -h/2+c, b/2-c],  # noqa: E501
              ['patch', 'quad', ConcretoC_Tag, NumDivCore_y, NumDivCore_z, -h/2+c, -b/2+c, h/2-c, -b/2+c, h/2-c, b/2-c, -h/2+c, b/2-c],  # noqa: E501
              
              #ConcretoC_Tag    MinMaxTag_concrete

              ['patch', 'quad', ConcretoNC_Tag_value, NumDivDir_y, NumDivDir_z, -h/2, -b/2, h/2, -b/2, h/2, -b/2+c, -h/2, -b/2+c],
              ['patch', 'quad', ConcretoNC_Tag_value, NumDivEsq_y, NumDivEsq_z, -h/2, b/2-c, h/2, b/2-c, h/2, b/2, -h/2, b/2],  
              ['patch', 'quad', ConcretoNC_Tag_value, NumDivInf_y, NumDivInf_z, -h/2, -b/2+c, -h/2+c, -b/2+c, -h/2+c, b/2-c, -h/2,b/2-c],
              ['patch', 'quad', ConcretoNC_Tag_value, NumDivSup_y, NumDivSup_z, h/2-c, -b/2+c, h/2, -b/2+c, h/2, b/2-c, h/2-c, b/2-c],
             
            #   ['patch', 'quad', MinMaxTag_UC, NumDivDir_y, NumDivDir_z, -h/2, -b/2, h/2, -b/2, h/2, -b/2+c, -h/2, -b/2+c],
            #   ['patch', 'quad', MinMaxTag_UC, NumDivEsq_y, NumDivEsq_z, -h/2, b/2-c, h/2, b/2-c, h/2, b/2, -h/2, b/2],  
            #   ['patch', 'quad', MinMaxTag_UC, NumDivInf_y, NumDivInf_z, -h/2, -b/2+c, -h/2+c, -b/2+c, -h/2+c, b/2-c, -h/2,b/2-c],
            #   ['patch', 'quad', MinMaxTag_UC, NumDivSup_y, NumDivSup_z, h/2-c, -b/2+c, h/2, -b/2+c, h/2, b/2-c, h/2-c, b/2-c],





              # ['layer', 'straight', Aco_Tag, 2, area_longitudinal, h/2-c, b/2-c, h/2-c, c-b/2],
              # ['layer', 'straight', Aco_Tag, 2, area_longitudinal, c-h/2, b/2-c, c-h/2, c-b/2],
              # # ['layer', 'straight', Aco_Tag, 2, Area_aco, 0.5*(h-2*c)/3.0, b/2-c, 0.5*(h-2*c)/3.0, c-b/2],
              # # ['layer', 'straight', Aco_Tag, 2, Area_aco, 0.5*(h-2*c)/3.0, b/2-c, 0.5*(h-2*c)/3.0, c-b/2]
             
              ]
    

    for ii in range(0, n_camadas):
        # fib_sec_1.append(['layer', 'straight', Aco_Tag, self.barras_camadas[ii], area_longitudinal, self.PosIniCam[ii], b/2-c, self.PosFinalCam[ii], c-b/2])
        # fib_sec_1.append(['layer', 'straight', Aco_Tag, barras_camadas[ii], area_longitudinal[ii], PosIniCam[ii], b/2-c, PosFinalCam[ii], c-b/2])
        if ii == 0:
            fib_sec_1.append(['layer', 'straight', MinMaxSteel_Tag[0], barras_camadas[ii], area_longitudinal[ii], PosIniCam[ii], b/2-c, PosFinalCam[ii], c-b/2])
            print('MinMaxSteel_Tag[0]:', MinMaxSteel_Tag[0], 'barras_camadas[ii]:', barras_camadas[ii], 'area_longitudinal[ii]:', area_longitudinal[ii], 'PosIniCam[ii]:', PosIniCam[ii], 'b/2-c:', b/2-c, 'PosFinalCam[ii]:', PosFinalCam[ii], 'c-b/2:', c-b/2)
        else:
            fib_sec_1.append(['layer', 'straight', MinMaxSteel_Tag[1], barras_camadas[ii], area_longitudinal[ii], PosIniCam[ii], b/2-c, PosFinalCam[ii], c-b/2])
            print('MinMaxSteel_Tag[1]:', MinMaxSteel_Tag[1], 'barras_camadas[ii]:', barras_camadas[ii], 'area_longitudinal[ii]:', area_longitudinal[ii], 'PosIniCam[ii]:', PosIniCam[ii], 'b/2-c:', b/2-c, 'PosFinalCam[ii]:', PosFinalCam[ii], 'c-b/2:', c-b/2)
    

    import opsvis as opsv
    opsv.fib_sec_list_to_cmds(fib_sec_1)
    
    #Essa lista de cores é necessário se você tiver diversos materiais e MatTags
    #Por exemplo, se você tiver um material com a MatTag = 100; Você precisará ter 100 elementos
    # na lista abaixo, senão dará erro.
    # matcolor = ['lightgrey', 'w', 'r', 'steelblue', 'b', 'g', 'm', 'w', 'r', 'y']
    # for ii in range(100):
    #     matcolor += ['w', 'r', 'steelblue', 'b', 'g', 'm', 'w', 'r', 'y']
    #     matcolor += ['w', 'r', 'steelblue', 'b', 'g', 'm', 'w', 'r', 'y']
    #     matcolor += ['w', 'r', 'steelblue', 'b', 'g', 'm', 'w', 'r', 'y']
    
    # opsv.plot_fiber_section(fib_sec_1, matcolor = matcolor)
    # plt.axis('equal')

    print("ConcretoC_Tag =", ConcretoC_Tag)
    print("ConcretoNC_Tag_value =", ConcretoNC_Tag_value)
    print("MinMaxSteel_Tag =", MinMaxSteel_Tag)

    matcolor_dict = {
        ConcretoC_Tag: 'red',               # concreto confinado
        ConcretoNC_Tag_value: 'lightgrey',  # concreto no confinado
        MinMaxSteel_Tag[0]: 'steelblue',    # acero capa 1
        MinMaxSteel_Tag[1]: 'steelblue'     # acero capa 2
    }

    opsv.plot_fiber_section(
        fib_sec_1,
        fillflag=1,
        matcolor_dict=matcolor_dict
    )
    plt.axis('equal')
    # plt.show()
        
    
    #No opensees deve aplicar esse comando antes de inserir no forcebeamcolumn
    ops.beamIntegration('Lobatto', IntegraTag, SectionTag, numIntgrPts)

    print('Sección ',SectionTag,' creada con éxito.')

    return IntegraTag,SectionTag,Ec,Ast,rho_cc,Ae,Acc,ke,rho_x,rho_y,flx,fly,A,B,fc_confinado,ec_confinado,xn,n,r,fc_inicial




print('Definido Secciones y Materiales')




class Alvenaria:
    def __init__(self, Alvenaria_Tag,
                 hcol_esq = 0.20, hcol_dir = 0.20, hvig_sup = 0.40, hvig_inf = 0.40,
                 tw_alv = 0.12, L_alv = 3, H_pav = 2.90, fm2 = 1.07, Em2 = None):
                 
        self.Alvenaria_Tag = Alvenaria_Tag
        self.hcol_esq = hcol_esq
        self.hcol_dir = hcol_dir
        self.hvig_sup = hvig_sup
        self.hvig_inf = hvig_inf
        self.L_alv = L_alv
        self.H_pav = H_pav
        self.tw_alv = tw_alv
        self.fm2 = fm2
        self.Em2 = Em2
        
    def criar_diagonal(self):
        
        #transformando para (mm)
        lw_alv = (self.L_alv - self.hcol_esq/2 - self.hcol_dir/2) *(1000)     #comprimento da alvenaria (vão - 0.5bpilar,esq - 0.5bpilar,dir)
        hw_alv = (self.H_pav - self.hvig_sup/2 - self.hvig_inf/2 ) *(1000)    #altura da alvenaria (pé direito - hviga,sup)
        ld_alv = ((self.L_alv**2 + self.H_pav**2)**(0.5)) *(1000)             #comprimento da treliça diagonal
        tw_alv = self.tw_alv          *(1000)                                 #espessura da alvenaria (mm)
        
        
        #Parâmetros:
        Ke_alv = 0.0143*(self.Em2**0.618)*(tw_alv**0.694)*((hw_alv/lw_alv)**(-1.096))    #kN/mm
        Fc_alv = 0.003766*(self.fm2**0.196)*(tw_alv**0.867)*(ld_alv**0.792)                   #kN
        dc_alv = 0.0154*(self.Em2**(-0.197))*((hw_alv/lw_alv)**0.978)*ld_alv                  #mm
        Kpc_alv = -1.278*(self.fm2**(-0.357))*(tw_alv**(-0.517))*(Ke_alv)                     #kN/mm     1000N/m    
        Fy_alv = 0.72*Fc_alv                                                                  #kN
        Fres_alv = 0.40*Fc_alv                                                                #kN
           
        
        # Tensão (Pontos do envelope negativo) #kN
        eNf1 = Fy_alv                #kN
        eNf3 = Fc_alv                #kN
        eNf4 = Fres_alv              #kN
        eNf2 = (eNf1 + eNf3) / 2     #kN
        
        # Deformação (Pontos do envelope negativo) (adimensional)
        eNd1 = eNf1/(Ke_alv*ld_alv)             
        eNd3 = dc_alv/ld_alv
        eNd4 = (eNf4 - eNf3)/(Kpc_alv*ld_alv) + eNd3
        eNd2 = (eNd1 + eNd3)/2
        
        
        # Tensões (Convertendo kN to N)
        eNf1 = eNf1 * 1000 #kN to N
        eNf3 = eNf3 * 1000 #kN to N    
        eNf4 = eNf4 * 1000 #kN to N
        eNf2 = eNf2 * 1000 #kN to N
        
        # plt.figure()
        # plt.scatter([0, -eNd1, -eNd2, -eNd3, -eNd4], [0, -eNf1, -eNf2, -eNf3, -eNf4])
        
        uForceN = 0.00; rDispN = 0.02; rForceN = 0.02; uForceP = 0.01; rDispP = 0.2; rForceP = 0.5;
        gK1 = 0.8;  gK2 = 0.7; gK3 = 0.7; gK4 = 0.7; gKLim = 0.95;
        gD1 = 0.2; gD2 = 0.2; gD3 = 0.2; gD4 = 0.2; gDLim = 0.1;  
        gE = 10; 
        gF1 = 0.5; gF2 = 0.5; gF3 = 0.5; gF4 = 0.5; gFLim = 0.5;  
        ePf1 = 0.00001; ePf2 = 0.00001; ePf3 = 0.00001; ePf4 = 0.00001;
        ePd1 = 0.000000001; ePd2 = 0.000000001; ePd3 = 0.000000001; ePd4 = 0.000000001;
        dmgType = 'cycle'
        
        
        ops.uniaxialMaterial('Pinching4', self.Alvenaria_Tag, ePf1, ePd1, ePf2, ePd2, ePf3, ePd3, ePf4, ePd4, -eNf1, -eNd1, -eNf2, -eNd2, -eNf3, -eNd3, -eNf4, -eNd4, rDispP, rForceP, uForceP, rDispN, rForceN, uForceN, gK1, gK2, gK3, gK4, gKLim, gD1, gD2, gD3, gD4, gDLim, gF1, gF2, gF3, gF4, gFLim, gE, dmgType)
        # print('ops.uniaxialMaterial("Pinching4",', self.Alvenaria_Tag,', ', ePf1,', ', ePd1,', ', ePf2,', ', ePd2,', ', ePf3,', ', ePd3,', ', ePf4,', ', ePd4,', ', -eNf1,', ', -eNd1,', ', -eNf2,', ', -eNd2,', ', -eNf3,', ', -eNd3,', ', -eNf4,', ', -eNd4,', ', rDispP,', ', rForceP,', ', uForceP,', ', rDispN,', ', rForceN,', ', uForceN,', ', gK1,', ', gK2,', ', gK3,', ', gK4,', ', gKLim,', ', gD1,', ', gD2,', ', gD3,', ', gD4,', ', gDLim,', ', gF1,', ', gF2,', ', gF3,', ', gF4,', ', gFLim,', ', gE,', ', dmgType,')')



























##############################################################
####################### RUN GEOMETRY #########################
##############################################################


# import matplotlib
# matplotlib.use('Agg')


# offset = 'No'
# exec(open('Sections_Materials.py').read())


#######################################################
# Iniciando temporizador para contar o tempo de analise 
########################################################
starttime = datetime.now()
aux = 0

# =============================================================================
#     Building the Model
# =============================================================================

ops.wipe()
ops.model('basic', '-ndm', 2)

# Geometric Transformations
BeamTransfTag = 1  # Elements along global X direction
ColTransfTag = 2  # Elements along global Y direction

# Beams
# ops.geomTransf('Corotational', BeamTransfTag)
# ops.geomTransf('Linear', BeamTransfTag)
ops.geomTransf('PDelta', BeamTransfTag) 

# Columns
# ops.geomTransf('Corotational', ColTransfTag) 
# ops.geomTransf('Linear', ColTransfTag) 
ops.geomTransf('PDelta', ColTransfTag) 

# Formulations
Formulation = 'forceBeamColumn' 
# Formulation = 'dispBeamColumn'


# =============================================================================
#                            Rigid Joints Offsets          
# =============================================================================

# Para los elementos que tienen parte rígida debido a la intersección viga-columna 

if offset == 'Yes':

    Tag_Offset_beam_left = 3
    Tag_Offset_beam_right = 4
    Tag_Offset_column_inf = 5
    Tag_Offset_column_sup = 6

    L_offset_beam = 0.356    # valores del paper = 
    L_offset_col = 0.075    # valores del paper =


    ops.geomTransf('Corotational',Tag_Offset_beam_left,'-jntOffset',L_offset_beam,0.0000001,0.0,0.0)  # Elemento 1: dibujado desde derecha a izquierda  
    ops.geomTransf('Corotational',Tag_Offset_beam_right,'-jntOffset',0.0,0.0,-L_offset_beam,0.0000001)  # Elemento 1: dibujado desde derecha a izquierda  
    ops.geomTransf('Corotational',Tag_Offset_column_inf,'-jntOffset',0.0,0.0,0.0,-L_offset_col)  # Elemento 1: dibujado desde derecha a izquierda  
    ops.geomTransf('Corotational',Tag_Offset_column_sup,'-jntOffset',0.0,0.0,0.0,-L_offset_col)  # Elemento 1: dibujado desde derecha a izquierda  

else:
    Tag_Offset_beam_left = BeamTransfTag
    Tag_Offset_beam_right = BeamTransfTag
    Tag_Offset_column_inf = ColTransfTag
    Tag_Offset_column_sup = ColTransfTag

# =============================================================================
#                            Integration Points          
# =============================================================================
numIntgrPts_extBeam = 2  # Ends of the beams
numIntgrPts_extInteriorBeam = 2  # Adjacent beams
numIntgrPts_middleBeam = 2     # Middle of the beams
numIntgrPts_extColumn = 2    # Ends of the columns
numIntgrPts_middleColumn = 2   # Middle of the columns


# pARA Formulación ForceBeamColumn
maxIter = 1000  # 10000  Estos parámetros no estpan afectando en nada el análisis
tol = 1e-6 # Estos parámetros no estpan afectando en nada el análisis

# =============================================================================
#                           Model Geometry Definition
# =============================================================================

# Spans and floor levels (meters)
X_spans = [0.0, 4.57]   # Spans in X direction [min=2] [max=9]  
Z_pavs = [0.0, 3.125]      # Floor levels [min=2] [max=99]



num_tramox = len(X_spans)
num_pav = len(Z_pavs)



######################################################
# Definición de los Materiales
######################################################


# Beams and columns



# Barra de 14 mm de diámetro
Material_Steel_14mm_Tag = 31     # Tag
MinMaxTag_steel_14mm = 32        # Tag
fy_normal_14mm = 450 #MPa        # estes tiene las barras de acero longitudinales
# MinStrain_Steel_8mm = -1000    # -0.098 
# MaxStrain_Steel_8mm = 1000   # 0.098
MinStrain_Steel_14mm = -0.098 
MaxStrain_Steel_14mm = 0.098
b_steel_14mm = 0.005                          # 0.000040551


# Barra de 10 mm de diámetro
Material_Steel_10mm_Tag = 33     # Tag
MinMaxTag_steel_10mm = 34        # Tag
fy_normal_10mm = 450 #400MPa   # estes tiene las barras de acero longitudinales
# MinStrain_Steel_10mm = -1000    # -0.122
# MaxStrain_Steel_10mm = 1000   # 0.122 
MinStrain_Steel_10mm = -0.122
MaxStrain_Steel_10mm = 0.122 
b_steel_10mm = 0.005                          # 0.0


# Barra de 22 mm de diámetro
Material_Steel_22mm_Tag = 35
MinMaxTag_steel_22mm = 36
fy_normal_22mm = 450 #462MPa   # estes tiene las barras de acero longitudinales
# MinStrain_Steel_12_5mm = -1000  # -0.16
# MaxStrain_Steel_12_5mm = 1000   #  0.16
MinStrain_Steel_22mm = -0.16
MaxStrain_Steel_22mm = 0.16
b_steel_12_5mm = 0.005   # 0.000049236

fyw_normal = 450 # Estribos

Es_normal = 200 # 201 GPa  # Modulo de elasticidade do aço
# Colocando altas resistencias del módulo de elasticidad del acero como 320 GPa no muda mucho la parte no lineal.


# =============================================================================
#                          Mesh Columns (Z)
# =============================================================================
Mid_discretiza_Col = 3   # Mesh size for the column middle zones   
Extremos_Inf_Discretiza_Col = 1 # Mesh size for the top end zones
Extremos_Sup_Discretiza_Col = 1   # Mesh size for the bottom end zones

# Column number  [1, 2, 3, 4]   from left to right             
Length_bottom =   [0.625]    # Length of the bottom of the column [m]
Length_top =  [0.625]   # Length of the top of the column [m]

# =============================================================================
#                          Mesh Beams (X)
# =============================================================================
Extremos_Discretiza_Beam = 1 # Mesh size for the beam end zones
Internos_Discretiza_Beam = 1   # Mesh size for the adjacent zones to the beam ends
Mid_discretiza_Beam = 2 # Mesh size for the beam middle zones

Length_beamsEnds =   [0.785] # Length of the beam ends [m]
Length_beamsEnds_internas =   [1.0] # Length of the adjacent zones to the beam ends [m]



############# Mesh size for the columns sections #############

NumDivCore_z_col = 1        # Confined Concrete
NumDivCore_y_col = 11       # Confined Concrete
NumDivInf_z_col = 1         # Unconfined Concrete - Bottom Z
NumDivInf_y_col = 2   #2    # Unconfined Concrete - Bottom Y
NumDivSup_z_col = 1         # Unconfined Concrete - Top Z
NumDivSup_y_col = 2   #2    # Unconfined Concrete - Top Y
NumDivDir_z_col = 1         # Unconfined Concrete - Right Z
NumDivDir_y_col = 16   #16  # Unconfined Concrete - Right Y
NumDivEsq_z_col = 1         # Unconfined Concrete - Left Z
NumDivEsq_y_col = 16   #16  # Unconfined Concrete - Left Y

############# Mesh size for the beams sections #############

NumDivCore_z_beam = 1        # Confined Concrete
NumDivCore_y_beam = 8       # Confined Concrete
NumDivInf_z_beam = 1         # Unconfined Concrete - Bottom Z
NumDivInf_y_beam = 2   #2    # Unconfined Concrete - Bottom Y
NumDivSup_z_beam = 1         # Unconfined Concrete - Top Z
NumDivSup_y_beam = 2   #2    # Unconfined Concrete - Top Y
NumDivDir_z_beam = 1         # Unconfined Concrete - Right Z
NumDivDir_y_beam = 16   #16  # Unconfined Concrete - Right Y
NumDivEsq_z_beam = 1         # Unconfined Concrete - Left Z
NumDivEsq_y_beam = 16   #16  # Unconfined Concrete - Left Y

##############################################################
#################### Type 1 column section - S5

# Sección sólo para el extremo inferior de la columna

fc_normal = 32 #MPa   # 33.9 34.3 Infill Frame

SectionTag_col_1 = 5
ColIntegraTag_1 = 5
ConcretoC_Tag_col1 = 8
ConcretoNC_Tag_col1 = 11

b_col = 0.35    
h_col = 0.35
cobrimento_col = 0.04  # 0.0762   # Cobrimento de la barra de acero en la columna

diam_sup_col = 0.022   # primera fibra superior

diam_mid_col = 0.022   # primeira fibra do meio

diam_inf_col = 0.022   # primera fibra inferior


nbarras_sup_col = 4
nbarras_mid_col = 2
nbarras_inf_col = 4
diam_transversal_col = 0.008 # diam estribos
espacamento_s_col = 0.09 # espaçamento dos estribos   


diam_longitudinal_value = [diam_sup_col, diam_inf_col, diam_mid_col]
# diam_longitudinal_value = [diam_sup_col, diam_inf_col]
barras_camadas_value = [nbarras_sup_col, nbarras_inf_col, nbarras_mid_col]
# barras_camadas_value = [nbarras_sup_col, nbarras_inf_col]
PosIniCam_value = [h_col/2-cobrimento_col, cobrimento_col-h_col/2, 0]
PosFinalCam_value = [h_col/2-cobrimento_col, cobrimento_col-h_col/2, 0]

# Se coloca primero el superior y luego el infeior
# Steel_Tag = [Material_Steel_Column_TopBars_Tag,Material_Steel_Column_BottomBars_Tag], MinMaxSteel_Tag = [MinMaxTag_steel_Column_TopBars,MinMaxTag_steel_Column_BottomBars]


IntegraTag,SectionTag,Ec,Ast,rho_cc,Ae,Acc,ke,rho_x,rho_y,flx,fly,A,B,fc_confinado,ec_confinado,xn,n,r,fc_uncon = sec_fibrasconfinadas(SectionTag = SectionTag_col_1, IntegraTag = ColIntegraTag_1, ConcretoC_Tag = ConcretoC_Tag_col1,ConcretoNC_Tag=ConcretoNC_Tag_col1, Steel_Tag = [Material_Steel_10mm_Tag,Material_Steel_10mm_Tag], MinMaxSteel_Tag = [MinMaxTag_steel_10mm,MinMaxTag_steel_10mm]  ,numIntgrPts=numIntgrPts_extColumn, 
                b_beam=b_col, h_beam=h_col, fc = fc_normal, cobrimento = cobrimento_col, 
                diam_longitudinal = diam_longitudinal_value , fy_ = [fy_normal_10mm,fy_normal_10mm] , Es_ =  Es_normal,
                    barras_camadas = barras_camadas_value, PosIniCam = PosIniCam_value, PosFinalCam = PosFinalCam_value,
                    diam_transversal = diam_transversal_col, espacamento_s = espacamento_s_col, npernas_xx = 4 , npernas_yy = 4, fy_transv = fyw_normal, MinStrain_Steel = [MinStrain_Steel_10mm,MinStrain_Steel_10mm] , MaxStrain_Steel = [MaxStrain_Steel_10mm,MaxStrain_Steel_10mm] ,b_steel = [b_steel_10mm,b_steel_10mm] ,NumDivCore_z = NumDivCore_z_col, NumDivCore_y = NumDivCore_y_col, NumDivInf_z = NumDivInf_z_col, NumDivInf_y = NumDivInf_y_col, NumDivSup_z = NumDivSup_z_col, NumDivSup_y = NumDivSup_y_col, NumDivDir_z = NumDivDir_z_col, NumDivDir_y = NumDivDir_y_col, NumDivEsq_z = NumDivEsq_z_col, NumDivEsq_y = NumDivEsq_y_col
                        )


# Print data of the constitutive properties of the concrete

print('###################################################################')
print('################### Confined Concrete - Column 1 -S5 ##################')
print('###################################################################')
print('###################################################################')
print('Intergration Tag = ', IntegraTag)
print('Section Tag = ', SectionTag)
print('Module of Elasticity = ', Ec)
print('Area of longitudinal reinforcement Ast = ', Ast)
print('Ratio of area of longitudinal reinforcement to area of core of section rho_cc = ', rho_cc)
print('Area of effectively confined concrete core Ae = ', Ae)
print('Area of concrete core Acc = ', Acc)
print('Coefinement effectively confined concrete core ke = ', ke)
print('Total area of transverse reinforcement parallel to the x axis rho_x = ', rho_x)
print('Total area of transverse reinforcement parallel to the y axis rho_y = ', rho_y)
print('Lateral confining stress on the concrete in the direction x flx = ', flx)
print('Lateral confining stress on the concrete in the direction y fly = ', fly)
print('A =',A)
print('B =',B)
print('Compressive Streght of Confined Concrete fcc = ', fc_confinado)
print('Strain of Confined Concrete ecc = ', ec_confinado)
print('xn = ', xn)
print('n = ', n)
print('r = ', r)
print('Compressive Streght of UNConfined Concrete fc = ', fc_uncon)   


##############################################################
#################### Type 2 column section -S6

# Sección sólo para el medio de la columna en el primer andar

# fc_normal_2 = 30.0  # Primeiro andar

SectionTag_col_2 = 6
ColIntegraTag_2 = 6
ConcretoC_Tag_col2 = 9
ConcretoNC_Tag_col2 = 12

b_col = 0.35    
h_col = 0.35
cobrimento_col = 0.04  # 0.0762   # Cobrimento de la barra de acero en la columna

diam_sup_col = 0.022   # primera fibra superior

diam_mid_col = 0.022   # primeira fibra do meio

diam_inf_col = 0.022   # primera fibra inferior


nbarras_sup_col = 4
nbarras_mid_col = 2
nbarras_inf_col = 4
diam_transversal_col = 0.008 # diam estribos
espacamento_s_col = 0.09 # espaçamento dos estribos   


diam_longitudinal_value = [diam_sup_col, diam_inf_col, diam_mid_col]
# diam_longitudinal_value = [diam_sup_col, diam_inf_col]
barras_camadas_value = [nbarras_sup_col, nbarras_inf_col, nbarras_mid_col]
# barras_camadas_value = [nbarras_sup_col, nbarras_inf_col]
PosIniCam_value = [h_col/2-cobrimento_col, cobrimento_col-h_col/2, 0]
PosFinalCam_value = [h_col/2-cobrimento_col, cobrimento_col-h_col/2, 0]

IntegraTag,SectionTag,Ec,Ast,rho_cc,Ae,Acc,ke,rho_x,rho_y,flx,fly,A,B,fc_confinado,ec_confinado,xn,n,r,fc_uncon = sec_fibrasconfinadas(SectionTag = SectionTag_col_2, IntegraTag = ColIntegraTag_2, ConcretoC_Tag = ConcretoC_Tag_col2, ConcretoNC_Tag=ConcretoNC_Tag_col2, Steel_Tag = [Material_Steel_10mm_Tag,Material_Steel_10mm_Tag] , MinMaxSteel_Tag = [MinMaxTag_steel_10mm,MinMaxTag_steel_10mm],numIntgrPts=numIntgrPts_middleColumn, 
                b_beam=b_col, h_beam=h_col, fc = fc_normal, cobrimento = cobrimento_col, 
                diam_longitudinal = diam_longitudinal_value , fy_ = [fy_normal_10mm,fy_normal_10mm], Es_ =  Es_normal,
                    barras_camadas = barras_camadas_value, PosIniCam = PosIniCam_value, PosFinalCam = PosFinalCam_value,
                    diam_transversal = diam_transversal_col, espacamento_s = espacamento_s_col, npernas_xx = 4 , npernas_yy = 4, fy_transv = fyw_normal, MinStrain_Steel = [MinStrain_Steel_10mm,MinStrain_Steel_10mm], MaxStrain_Steel = [MaxStrain_Steel_10mm,MaxStrain_Steel_10mm],b_steel = [b_steel_10mm,b_steel_10mm],NumDivCore_z = NumDivCore_z_col, NumDivCore_y = NumDivCore_y_col, NumDivInf_z = NumDivInf_z_col, NumDivInf_y = NumDivInf_y_col, NumDivSup_z = NumDivSup_z_col, NumDivSup_y = NumDivSup_y_col, NumDivDir_z = NumDivDir_z_col, NumDivDir_y = NumDivDir_y_col, NumDivEsq_z = NumDivEsq_z_col, NumDivEsq_y = NumDivEsq_y_col
                        )


# Print data of the constitutive properties of the concrete

print('###################################################################')
print('################### Confined Concrete - Column 2 - S6 ##################')
print('###################################################################')
print('###################################################################')
print('Intergration Tag = ', IntegraTag)
print('Section Tag = ', SectionTag)
print('Module of Elasticity = ', Ec)
print('Area of longitudinal reinforcement Ast = ', Ast)
print('Ratio of area of longitudinal reinforcement to area of core of section rho_cc = ', rho_cc)
print('Area of effectively confined concrete core Ae = ', Ae)
print('Area of concrete core Acc = ', Acc)
print('Coefinement effectively confined concrete core ke = ', ke)
print('Total area of transverse reinforcement parallel to the x axis rho_x = ', rho_x)
print('Total area of transverse reinforcement parallel to the y axis rho_y = ', rho_y)
print('Lateral confining stress on the concrete in the direction x flx = ', flx)
print('Lateral confining stress on the concrete in the direction y fly = ', fly)
print('A =',A)
print('B =',B)
print('Compressive Streght of Confined Concrete fcc = ', fc_confinado)
print('Strain of Confined Concrete ecc = ', ec_confinado)
print('xn = ', xn)
print('n = ', n)
print('r = ', r)
print('Compressive Streght of UNConfined Concrete fc = ', fc_uncon)   
                     
Ebc = Ec / 10**6 #MPa
 


# =============================================================================
#                         Beam Definition (X)
# =============================================================================

##############################################################
#################### Type 1 beam section - Section B3

# Sección sólo para los extremos de las vigas 

# fc_normal_4 = 30.0 

SectionTag_beam_1 = 1 # Section tag
BeamIntegraTag_1 = 1 # Integration tag
ConcretoC_Tag_beam1 = 4  # Confined concrete tag. This tag is different the others sections because each section has a different stirrup spacing and therefore a different confinement effect.
ConcretoNC_Tag_beam1 = 14 # Unconfined concrete tag

b_beam = 0.20      # Width of the beam (m)
h_beam = 0.40      # Height of the beam (m)
cobrimento_beam = 0.04  # Cover of the steel bars (m)

diam_sup_beam_1 = 0.0125  # Diameter of the upper steel bars (m)
diam_inf_beam_1 = 0.008  # Diameter of the lower steel bars (m)
nbarras_sup_beam = 4    # Number of upper steel bars
nbarras_inf_beam = 4    # Number of lower steel bars
diam_transversal_beam = 0.005  # Diameter of the transverse steel bars (m)
espacamento_s_beam = 0.16  # Spacing of the transverse steel bars (m)


diam_longitudinal_value = [diam_sup_beam_1, diam_inf_beam_1]
barras_camadas_value = [nbarras_sup_beam, nbarras_inf_beam]
PosIniCam_value= [h_beam/2-cobrimento_beam, cobrimento_beam-h_beam/2]
PosFinalCam_value = [h_beam/2-cobrimento_beam, cobrimento_beam-h_beam/2]

IntegraTag,SectionTag,Ec,Ast,rho_cc,Ae,Acc,ke,rho_x,rho_y,flx,fly,A,B,fc_confinado,ec_confinado,xn,n,r,fc_uncon = sec_fibrasconfinadas(SectionTag = SectionTag_beam_1, IntegraTag = BeamIntegraTag_1 , ConcretoC_Tag = ConcretoC_Tag_beam1,ConcretoNC_Tag=ConcretoNC_Tag_beam1,Steel_Tag = [Material_Steel_12_5mm_Tag,Material_Steel_8mm_Tag], MinMaxSteel_Tag = [MinMaxTag_steel_12_5mm,MinMaxTag_steel_8mm] , numIntgrPts=numIntgrPts_extBeam, 
                b_beam=b_beam, h_beam=h_beam, fc = fc_normal, cobrimento = cobrimento_beam, 
                diam_longitudinal = diam_longitudinal_value , fy_ = [fy_normal_12_5mm, fy_normal_8mm], Es_ =  Es_normal,
                    barras_camadas = barras_camadas_value, PosIniCam = PosIniCam_value, PosFinalCam = PosFinalCam_value,
                    diam_transversal = diam_transversal_beam, espacamento_s = espacamento_s_beam, npernas_xx = 2 , npernas_yy = 2, fy_transv = fyw_normal, MinStrain_Steel = [MinStrain_Steel_12_5mm, MinStrain_Steel_8mm], MaxStrain_Steel = [MaxStrain_Steel_12_5mm, MaxStrain_Steel_8mm], b_steel = [b_steel_12_5mm, b_steel_8mm], NumDivCore_z = NumDivCore_z_beam, NumDivCore_y = NumDivCore_y_beam, NumDivInf_z = NumDivInf_z_beam, NumDivInf_y = NumDivInf_y_beam, NumDivSup_z = NumDivSup_z_beam, NumDivSup_y = NumDivSup_y_beam, NumDivDir_z = NumDivDir_z_beam, NumDivDir_y = NumDivDir_y_beam, NumDivEsq_z = NumDivEsq_z_beam, NumDivEsq_y = NumDivEsq_y_beam
                        )


# Print data of the constitutive properties of the concrete

print('###################################################################')
print('################### Confined Concrete - Section B3 ####################')
print('###################################################################')
print('###################################################################')
print('Intergration Tag = ', IntegraTag)
print('Section Tag = ', SectionTag)
print('Module of Elasticity = ', Ec)
print('Area of longitudinal reinforcement Ast = ', Ast)
print('Ratio of area of longitudinal reinforcement to area of core of section rho_cc = ', rho_cc)
print('Area of effectively confined concrete core Ae = ', Ae)
print('Area of concrete core Acc = ', Acc)
print('Coefinement effectively confined concrete core ke = ', ke)
print('Total area of transverse reinforcement parallel to the x axis rho_x = ', rho_x)
print('Total area of transverse reinforcement parallel to the y axis rho_y = ', rho_y)
print('Lateral confining stress on the concrete in the direction x flx = ', flx)
print('Lateral confining stress on the concrete in the direction y fly = ', fly)
print('A =',A)
print('B =',B)
print('Compressive Streght of Confined Concrete fcc = ', fc_confinado)
print('Strain of Confined Concrete ecc = ', ec_confinado)
print('xn = ', xn)
print('n = ', n)
print('r = ', r)
print('Compressive Streght of UNConfined Concrete fc = ', fc_uncon)    

##############################################################
#################### Type 3 beam section - B2

# Sección para el medio de las vigas  del primer andar

# fc_normal_6 = 30.0


SectionTag_beam_3 = 3
BeamIntegraTag_3 = 3
ConcretoC_Tag_beam3 = 6  # Confined concrete tag. this tag is different because in this case each section has a different spacing of the stirrups
ConcretoNC_Tag_beam3 = 16


b_beam = 0.20           
h_beam = 0.40 
cobrimento_beam = 0.04
 
diam_sup_beam_3 = 0.008
diam_inf_beam_3 = 0.008
nbarras_sup_beam = 2
nbarras_inf_beam = 4
diam_transversal_beam = 0.005
espacamento_s_beam_int = 0.16  

diam_longitudinal_value = [diam_sup_beam_3, diam_inf_beam_3]
barras_camadas_value = [nbarras_sup_beam, nbarras_inf_beam]
PosIniCam_value= [h_beam/2-cobrimento_beam, cobrimento_beam-h_beam/2]
PosFinalCam_value = [h_beam/2-cobrimento_beam, cobrimento_beam-h_beam/2]

IntegraTag,SectionTag,Ec,Ast,rho_cc,Ae,Acc,ke,rho_x,rho_y,flx,fly,A,B,fc_confinado,ec_confinado,xn,n,r,fc_uncon = sec_fibrasconfinadas(SectionTag = SectionTag_beam_3, IntegraTag = BeamIntegraTag_3 , ConcretoC_Tag = ConcretoC_Tag_beam3,ConcretoNC_Tag=ConcretoNC_Tag_beam3, Steel_Tag = [Material_Steel_8mm_Tag,Material_Steel_8mm_Tag],MinMaxSteel_Tag = [MinMaxTag_steel_8mm,MinMaxTag_steel_8mm], numIntgrPts=numIntgrPts_middleBeam, 
                b_beam=b_beam, h_beam=h_beam, fc = fc_normal, cobrimento = cobrimento_beam, 
                diam_longitudinal = diam_longitudinal_value , fy_ = [fy_normal_8mm, fy_normal_8mm], Es_ =  Es_normal,
                    barras_camadas = barras_camadas_value, PosIniCam = PosIniCam_value, PosFinalCam = PosFinalCam_value,
                    diam_transversal = diam_transversal_beam, espacamento_s = espacamento_s_beam_int, npernas_xx = 2 , npernas_yy = 2, fy_transv = fyw_normal,  MinStrain_Steel = [MinStrain_Steel_8mm, MinStrain_Steel_8mm], MaxStrain_Steel = [MaxStrain_Steel_8mm, MaxStrain_Steel_8mm], b_steel = [b_steel_8mm, b_steel_8mm],NumDivCore_z = NumDivCore_z_beam, NumDivCore_y = NumDivCore_y_beam, NumDivInf_z = NumDivInf_z_beam, NumDivInf_y = NumDivInf_y_beam, NumDivSup_z = NumDivSup_z_beam, NumDivSup_y = NumDivSup_y_beam, NumDivDir_z = NumDivDir_z_beam, NumDivDir_y = NumDivDir_y_beam, NumDivEsq_z = NumDivEsq_z_beam, NumDivEsq_y = NumDivEsq_y_beam
                        )


# Print data of the constitutive properties of the concrete

print('###################################################################')
print('################### Confined Concrete - Section B2 ####################')
print('###################################################################')
print('###################################################################')
print('Intergration Tag = ', IntegraTag)
print('Section Tag = ', SectionTag)
print('Module of Elasticity = ', Ec)
print('Area of longitudinal reinforcement Ast = ', Ast)
print('Ratio of area of longitudinal reinforcement to area of core of section rho_cc = ', rho_cc)
print('Area of effectively confined concrete core Ae = ', Ae)
print('Area of concrete core Acc = ', Acc)
print('Coefinement effectively confined concrete core ke = ', ke)
print('Total area of transverse reinforcement parallel to the x axis rho_x = ', rho_x)
print('Total area of transverse reinforcement parallel to the y axis rho_y = ', rho_y)
print('Lateral confining stress on the concrete in the direction x flx = ', flx)
print('Lateral confining stress on the concrete in the direction y fly = ', fly)
print('A =',A)
print('B =',B)
print('Compressive Streght of Confined Concrete fcc = ', fc_confinado)
print('Strain of Confined Concrete ecc = ', ec_confinado)
print('xn = ', xn)
print('n = ', n)
print('r = ', r)
print('Compressive Streght of UNConfined Concrete fc = ', fc_uncon) 


##############################################################
#################### Type 2 beam section - B1


# Sección adyacentes a los extremos de las vigas

# fc_normal_5 = 30.0

SectionTag_beam_2 = 2
BeamIntegraTag_2 = 2
ConcretoC_Tag_beam2 = 5  # Confined concrete tag. this tag is different because in this case each section has a different spacing of the stirrups
ConcretoNC_Tag_beam2 = 15

b_beam = 0.20            
h_beam = 0.40   
cobrimento_beam = 0.04
      
diam_sup_beam_2 = 0.010
diam_inf_beam_2 = 0.008
nbarras_sup_beam = 4
nbarras_inf_beam = 4
diam_transversal_beam = 0.005
espacamento_s_beam = 0.16  


diam_longitudinal_value = [diam_sup_beam_2, diam_inf_beam_2]
barras_camadas_value = [nbarras_sup_beam, nbarras_inf_beam]
PosIniCam_value= [h_beam/2-cobrimento_beam, cobrimento_beam-h_beam/2]
PosFinalCam_value = [h_beam/2-cobrimento_beam, cobrimento_beam-h_beam/2]

IntegraTag,SectionTag,Ec,Ast,rho_cc,Ae,Acc,ke,rho_x,rho_y,flx,fly,A,B,fc_confinado,ec_confinado,xn,n,r,fc_uncon = sec_fibrasconfinadas(SectionTag = SectionTag_beam_2, IntegraTag = BeamIntegraTag_2 , ConcretoC_Tag = ConcretoC_Tag_beam2, ConcretoNC_Tag=ConcretoNC_Tag_beam2, Steel_Tag = [Material_Steel_10mm_Tag,Material_Steel_8mm_Tag],MinMaxSteel_Tag = [MinMaxTag_steel_10mm,MinMaxTag_steel_8mm] ,numIntgrPts=numIntgrPts_extInteriorBeam, 
                b_beam=b_beam, h_beam=h_beam, fc = fc_normal, cobrimento = cobrimento_beam, 
                diam_longitudinal = diam_longitudinal_value , fy_ = [fy_normal_10mm, fy_normal_8mm], Es_ =  Es_normal,
                    barras_camadas = barras_camadas_value, PosIniCam = PosIniCam_value, PosFinalCam = PosFinalCam_value,
                    diam_transversal = diam_transversal_beam, espacamento_s = espacamento_s_beam, npernas_xx = 2 , npernas_yy = 2, fy_transv = fyw_normal,  MinStrain_Steel = [MinStrain_Steel_10mm, MinStrain_Steel_8mm], MaxStrain_Steel = [MaxStrain_Steel_10mm, MaxStrain_Steel_8mm], b_steel = [b_steel_10mm, b_steel_8mm],NumDivCore_z = NumDivCore_z_beam, NumDivCore_y = NumDivCore_y_beam, NumDivInf_z = NumDivInf_z_beam, NumDivInf_y = NumDivInf_y_beam, NumDivSup_z = NumDivSup_z_beam, NumDivSup_y = NumDivSup_y_beam, NumDivDir_z = NumDivDir_z_beam, NumDivDir_y = NumDivDir_y_beam, NumDivEsq_z = NumDivEsq_z_beam, NumDivEsq_y = NumDivEsq_y_beam
                        )


# Print data of the constitutive properties of the concrete

print('###################################################################')
print('################### Confined Concrete - Section B1 ####################')
print('###################################################################')
print('###################################################################')
print('Intergration Tag = ', IntegraTag)
print('Section Tag = ', SectionTag)
print('Module of Elasticity = ', Ec)
print('Area of longitudinal reinforcement Ast = ', Ast)
print('Ratio of area of longitudinal reinforcement to area of core of section rho_cc = ', rho_cc)
print('Area of effectively confined concrete core Ae = ', Ae)
print('Area of concrete core Acc = ', Acc)
print('Coefinement effectively confined concrete core ke = ', ke)
print('Total area of transverse reinforcement parallel to the x axis rho_x = ', rho_x)
print('Total area of transverse reinforcement parallel to the y axis rho_y = ', rho_y)
print('Lateral confining stress on the concrete in the direction x flx = ', flx)
print('Lateral confining stress on the concrete in the direction y fly = ', fly)
print('A =',A)
print('B =',B)
print('Compressive Streght of Confined Concrete fcc = ', fc_confinado)
print('Strain of Confined Concrete ecc = ', ec_confinado)
print('xn = ', xn)
print('n = ', n)
print('r = ', r)
print('Compressive Streght of UNConfined Concrete fc = ', fc_uncon)    


     

# ##############################################################
# #################### Type 4 beam section - S4

# # Sección sólo para el medio de las vigas del segundo andar

# fc_normal_7 = 32.0

# SectionTag_beam_4 = 4
# BeamIntegraTag_4 = 4
# ConcretoC_Tag_beam4 = 7  # Confined concrete tag. this tag is different because in this case each section has a different spacing of the stirrups
# ConcretoNC_Tag_beam4 = 17

# b_beam = 0.090            
# h_beam = 0.140    
# cobrimento_beam = 0.007
      
# diam_sup_beam = 0.010
# diam_inf_beam = 0.010
# nbarras_sup_beam = 2
# nbarras_inf_beam = 2
# diam_transversal_beam = 0.006 
# espacamento_s_beam_int = 0.130  # PAPER34 = 67mm

# diam_longitudinal_value = [diam_sup_beam, diam_inf_beam]
# barras_camadas_value = [nbarras_sup_beam, nbarras_inf_beam]
# PosIniCam_value= [h_beam/2-cobrimento_beam, cobrimento_beam-h_beam/2]
# PosFinalCam_value = [h_beam/2-cobrimento_beam, cobrimento_beam-h_beam/2]

# IntegraTag,SectionTag,Ec,Ast,rho_cc,Ae,Acc,ke,rho_x,rho_y,flx,fly,A,B,fc_confinado,ec_confinado,xn,n,r,fc_uncon = sec_fibrasconfinadas(SectionTag = SectionTag_beam_4, IntegraTag = BeamIntegraTag_4 , ConcretoC_Tag = ConcretoC_Tag_beam4,ConcretoNC_Tag=ConcretoNC_Tag_beam4, numIntgrPts=numIntgrPts_middleBeam, 
#                 b_beam=b_beam, h_beam=h_beam, fc = fc_normal_7, cobrimento = cobrimento_beam, 
#                 diam_longitudinal = diam_longitudinal_value , fy_ = fy_normal, Es_ =  Es_normal,
#                     barras_camadas = barras_camadas_value, PosIniCam = PosIniCam_value, PosFinalCam = PosFinalCam_value,
#                     diam_transversal = diam_transversal_beam, espacamento_s = espacamento_s_beam_int, npernas_xx = 2 , npernas_yy = 2, fy_transv = fyw_normal, MinMaxTag_CC = 607,MinMaxTag_UC=707,NumDivCore_z = NumDivCore_z_beam, NumDivCore_y = NumDivCore_y_beam, NumDivInf_z = NumDivInf_z_beam, NumDivInf_y = NumDivInf_y_beam, NumDivSup_z = NumDivSup_z_beam, NumDivSup_y = NumDivSup_y_beam, NumDivDir_z = NumDivDir_z_beam, NumDivDir_y = NumDivDir_y_beam, NumDivEsq_z = NumDivEsq_z_beam, NumDivEsq_y = NumDivEsq_y_beam
#                         )


# # Print data of the constitutive properties of the concrete

# print('###################################################################')
# print('################### Confined Concrete - Beam 4 - S4 ####################')
# print('###################################################################')
# print('###################################################################')
# print('Intergration Tag = ', IntegraTag)
# print('Section Tag = ', SectionTag)
# print('Module of Elasticity = ', Ec)
# print('Area of longitudinal reinforcement Ast = ', Ast)
# print('Ratio of area of longitudinal reinforcement to area of core of section rho_cc = ', rho_cc)
# print('Area of effectively confined concrete core Ae = ', Ae)
# print('Area of concrete core Acc = ', Acc)
# print('Coefinement effectively confined concrete core ke = ', ke)
# print('Total area of transverse reinforcement parallel to the x axis rho_x = ', rho_x)
# print('Total area of transverse reinforcement parallel to the y axis rho_y = ', rho_y)
# print('Lateral confining stress on the concrete in the direction x flx = ', flx)
# print('Lateral confining stress on the concrete in the direction y fly = ', fly)
# print('A =',A)
# print('B =',B)
# print('Compressive Streght of Confined Concrete fcc = ', fc_confinado)
# print('Strain of Confined Concrete ecc = ', ec_confinado)
# print('xn = ', xn)
# print('n = ', n)
# print('r = ', r)
# print('Compressive Streght of UNConfined Concrete fc = ', fc_uncon)  

# =============================================================================
#                            Criação dos Pilares (Y)         
# =============================================================================

# Determinando os Nós e os Elementos Pilares

#OJO REVISAR LA SEPARCION DE LOS ESTRIBOS EN LA BASE DE LA COLUMNA, YA QUE NO CREO QUE LAS COLUMNAS DEL SEGUNDAR ANDAR TIENEN DOS TIPOS DE SEPARACION.

Discretiza_resta = Mid_discretiza_Col - Extremos_Inf_Discretiza_Col #Para las columnas del primer piso

total_elements = Extremos_Inf_Discretiza_Col + Mid_discretiza_Col + Extremos_Sup_Discretiza_Col




Length_middle = []

for pav in range(1, num_pav):  # Para cada intervalo vertical entre pavimentos
    altura_inferior = Z_pavs[pav-1]
    altura_superior = Z_pavs[pav]
    altura_total = altura_superior - altura_inferior 
    
    # Para cada tramo en x
    middle_por_tramo = []
    for tramox in range(num_tramox):
        length_mid = altura_total - Length_bottom[tramox] - Length_top[tramox]
        middle_por_tramo.append(length_mid)
    Length_middle.append(middle_por_tramo)

# Length_middle es una lista de listas: 
# cada elemento corresponde a un pavimento y dentro tiene un arreglo con longitudes medias por tramo
print("Length_middle:", Length_middle)

# Length_middle: [[0.376, 0.376, 0.376], [0.3710000000000001, 0.3710000000000001, 0.3710000000000001], [0.371, 0.371, 0.371]]   Length_middle[pav][tramox] 
eleColumn_section_map = {}
for pav in range(1,num_pav+1):
    for tramox in range(1,num_tramox+1):
        
        # Crea todos los NODOS PRINCIPALES de la estructura (intersecciones de vigas y columnas).
        ops.node(int(str(pav)+str(0)+str(tramox)), X_spans[tramox-1], (Z_pavs[pav-1]))

        # Crea todos los nodos internos de las columnas (los nodos principales (intersecciones de vigas y columnas) ya fueron creados en el bucle anterior).)

        for discretiza in range(1,total_elements):
            if pav < num_pav:
                if discretiza < Extremos_Inf_Discretiza_Col+1:
                    ops.node(int(str(pav)+str(0)+str(tramox)+str(0)+str(2)+str(discretiza)), X_spans[tramox-1], Z_pavs[pav-1]+Length_bottom[tramox-1]*discretiza/Extremos_Inf_Discretiza_Col)
                elif discretiza > Extremos_Inf_Discretiza_Col and discretiza < (Extremos_Inf_Discretiza_Col + Mid_discretiza_Col + 1):
                    ops.node(int(str(pav)+str(0)+str(tramox)+str(0)+str(2)+str(discretiza)), X_spans[tramox-1], Z_pavs[pav-1]+Length_bottom[tramox-1]+Length_middle[pav-1][tramox-1]*(discretiza-Extremos_Inf_Discretiza_Col)/Mid_discretiza_Col)
                else:
                    ops.node(int(str(pav)+str(0)+str(tramox)+str(0)+str(2)+str(discretiza)), X_spans[tramox-1], Z_pavs[pav-1]+Length_bottom[tramox-1]+Length_middle[pav-1][tramox-1]+((discretiza-Extremos_Inf_Discretiza_Col-Mid_discretiza_Col)/Extremos_Sup_Discretiza_Col)*Length_top[tramox-1])



ColIntegraTag_ext = ColIntegraTag_1        # Extremo
ColIntegraTag_mid = ColIntegraTag_2

for pav in range(1, num_pav):  # Hasta el penúltimo pavimento
    for tramox in range(1, num_tramox+1): 

        # === PRIMER ELEMENTO: nodo principal (intersección) a primer nodo interno ===
        nodo_i = int(str(pav) + str(0) + str(tramox))  # nodo principal de intersección
        nodo_j = int(str(pav) + str(0) + str(tramox) + str(0) + str(2) + "1")  # primer nodo interno
        eleTag = int(str(pav) + str(0) + str(tramox) + str(0) + str(0) + str(2) + "1")

        if Formulation == 'dispBeamColumn':
            ops.element(Formulation, eleTag, nodo_i, nodo_j, ColTransfTag, ColIntegraTag_ext)

        else:
            ops.element(Formulation, eleTag, nodo_i, nodo_j, ColTransfTag, ColIntegraTag_ext, 'iter', maxIter, tol)
            # print('Elemento: ', eleTag, ' Nodo_i: ', nodo_i, ' Nodo_j: ', nodo_j, ' ColTransfTag: ', ColTransfTag, ' ColIntegraTag: ', ColIntegraTag_ext)

        eleColumn_section_map[eleTag] = ColIntegraTag_ext

        # === RESTO DE ELEMENTOS: entre nodos internos ===
        for discretiza in range(2, total_elements):
            # print('Pavimento: ', pav, ' Tramo: ', tramox, ' Discretiza: ', discretiza)
            nodo_i = int(str(pav) + str(0) + str(tramox) + str(0) + str(2) + str(discretiza - 1))
            nodo_j = int(str(pav) + str(0) + str(tramox) + str(0) + str(2) + str(discretiza))
            eleTag = int(str(pav) + str(0) + str(tramox) + str(0) + str(0) + str(2) + str(discretiza))

            if discretiza <= Extremos_Inf_Discretiza_Col or discretiza > Extremos_Inf_Discretiza_Col + Mid_discretiza_Col:
                ColIntegraTag = ColIntegraTag_ext
                # print('Valor del discretiza', discretiza)
                # print('Entro al Extremo Columna', ColIntegraTag)
            else:
                ColIntegraTag = ColIntegraTag_mid
                # print('Valor del discretiza', discretiza)
                # print('Entro a la columna media', ColIntegraTag) 

            if Formulation == 'dispBeamColumn':
                ops.element(Formulation, eleTag, nodo_i, nodo_j, ColTransfTag, ColIntegraTag)
            else:
                ops.element(Formulation, eleTag, nodo_i, nodo_j, ColTransfTag, ColIntegraTag, 'iter', maxIter, tol)

            eleColumn_section_map[eleTag] = ColIntegraTag

        # === ÚLTIMO ELEMENTO: último nodo interno até nodo principal do pavimento superior ===
        nodo_i = int(str(pav) + str(0) + str(tramox) + str(0) + str(2) + str(total_elements - 1))
        nodo_j = int(str(pav + 1) + str(0) + str(tramox))  # nodo principal del pavimento superior
        eleTag = int(str(pav) + str(0) + str(tramox) + str(0) + str(0) + str(2) + str(total_elements))

        if Formulation == 'dispBeamColumn':
            ops.element(Formulation, eleTag, nodo_i, nodo_j, ColTransfTag, ColIntegraTag_ext)
        else:
            ops.element(Formulation, eleTag, nodo_i, nodo_j, ColTransfTag, ColIntegraTag_ext, 'iter', maxIter, tol)

        eleColumn_section_map[eleTag] = ColIntegraTag_ext

             
# =============================================================================
#                            Criação das Vigas (X)          
# =============================================================================

# -----------------------------------------------------------------------------
# TABLA DE CONFIGURACIÓN DE SECCIONES POR VIGA
# -----------------------------------------------------------------------------
# Permite asignar una sección distinta a cada zona de cada viga de forma
# independiente, sin modificar la lógica del loop de creación de elementos.
#
# Zonas disponibles por viga (de izquierda a derecha):
#   'ext_izq'  -> extremo izquierdo          (usa BeamIntegraTag_1 por defecto)
#   'int_izq'  -> zona interna izquierda      (usa BeamIntegraTag_2 por defecto)
#   'mid'      -> zona central                (usa BeamIntegraTag_3 por defecto)
#   'int_der'  -> zona interna derecha        (usa BeamIntegraTag_2 por defecto)
#   'ext_der'  -> extremo derecho             (usa BeamIntegraTag_1 por defecto)
#
# Clave del diccionario: (pav, tramox)
#   pav    -> número de pavimento (empieza en 2, siendo el primer nivel con vigas)
#   tramox -> tramo de viga (1 = viga entre columna 1 y 2, de izquierda a derecha)
#
# INSTRUCCIONES DE USO:
#   1. Todas las vigas se inicializan con la configuración por defecto (simétrica).
#   2. Para cambiar una viga específica, sobreescribí su entrada después del bloque
#      de inicialización, usando solo las zonas que quieras modificar.
#
# Ejemplos:
#   # Cambiar solo el extremo izquierdo de la viga del piso 2, tramo 1:
#   beam_section_config[(2, 1)]['ext_izq'] = BeamIntegraTag_A
#
#   # Viga con extremos completamente distintos:
#   beam_section_config[(3, 2)]['ext_izq'] = BeamIntegraTag_A
#   beam_section_config[(3, 2)]['ext_der'] = BeamIntegraTag_B
# -----------------------------------------------------------------------------

def _beam_config_default(tag_ext, tag_int, tag_mid):
    """Genera una configuración simétrica por defecto para una viga."""
    return {
        'ext_izq': tag_ext,
        'int_izq': tag_int,
        'mid':     tag_mid,
        'int_der': tag_int,
        'ext_der': tag_ext,
    }

# Inicializar todas las vigas con la configuración por defecto
beam_section_config = {}
for _pav in range(2, num_pav + 1):
    for _tramox in range(1, num_tramox):
        beam_section_config[(_pav, _tramox)] = _beam_config_default(
            BeamIntegraTag_1,   # extremos
            BeamIntegraTag_2,   # internos
            BeamIntegraTag_3,   # centro
        )

# -----------------------------------------------------------------------------
# EXCEPCIONES: sobreescribir aquí las vigas que difieren del default
# -----------------------------------------------------------------------------
# Ejemplo — viga del piso 2, tramo 1, con extremos diferentes entre sí:
# beam_section_config[(2, 1)]['ext_izq'] = BeamIntegraTag_1
# beam_section_config[(2, 1)]['ext_der'] = BeamIntegraTag_1   # cambiar por otro tag si es diferente


# ANDAR 1
beam_section_config[(2, 1)]['ext_izq'] = BeamIntegraTag_2
beam_section_config[(3, 1)]['ext_izq'] = BeamIntegraTag_2   
beam_section_config[(4, 1)]['ext_izq'] = BeamIntegraTag_2  

beam_section_config[(2, 1)]['int_der'] = BeamIntegraTag_1
beam_section_config[(3, 1)]['int_der'] = BeamIntegraTag_1   
beam_section_config[(4, 1)]['int_der'] = BeamIntegraTag_1   

# ANDAR 2
beam_section_config[(2, 2)]['int_izq'] = BeamIntegraTag_1
beam_section_config[(2, 2)]['int_der'] = BeamIntegraTag_1

# ANDAR 3
beam_section_config[(2, 3)]['int_izq'] = BeamIntegraTag_1
beam_section_config[(3, 3)]['int_izq'] = BeamIntegraTag_1   
beam_section_config[(4, 3)]['int_izq'] = BeamIntegraTag_1  

beam_section_config[(2, 3)]['ext_der'] = BeamIntegraTag_2
beam_section_config[(3, 3)]['ext_der'] = BeamIntegraTag_2  
beam_section_config[(4, 3)]['ext_der'] = BeamIntegraTag_2   



#
# Ejemplo — reemplazar la config completa de una viga:
                                           # Extremos Izquierdo,      interior izquiero, centro      # se repite de forma simétrica para la derecha
# beam_section_config[(3, 2)] = _beam_config_default(BeamIntegraTag_A, BeamIntegraTag_2, BeamIntegraTag_3)   # Siemper crea una configuración simétrica, luego se pueden modificar las zonas específicas si se desea
# beam_section_config[(3, 2)]['ext_der'] = BeamIntegraTag_B    # Se modifica la zona específica del extremo derecho para que sea diferente al izquierdo
# -----------------------------------------------------------------------------


total_elements_beam = 2 * Extremos_Discretiza_Beam + 2 * Internos_Discretiza_Beam + Mid_discretiza_Beam
eleBeam_section_map = {}

for pav in range(2, num_pav + 1):  # Para cada pavimento
    y_coord = Z_pavs[pav - 1]

    for tramox in range(1, num_tramox):  # Cada tramo entre columnas (de izquierda a derecha)
        x_ini = X_spans[tramox - 1]
        x_fin = X_spans[tramox]
        length_total = x_fin - x_ini

        # Longitudes
        length_ext = Length_beamsEnds[tramox - 1]
        length_int = Length_beamsEnds_internas[tramox - 1]
        length_mid = length_total - 2 * length_ext - 2 * length_int

        # === CREACIÓN DE NODOS INTERNOS DE LAS VIGAS ===
        for discretiza in range(1, total_elements_beam):
            if discretiza <= Extremos_Discretiza_Beam:
                # Extremo izquierdo
                x = x_ini + (length_ext / Extremos_Discretiza_Beam) * discretiza

            elif discretiza <= Extremos_Discretiza_Beam + Internos_Discretiza_Beam:
                # Interna izquierda
                x = x_ini + length_ext + (length_int / Internos_Discretiza_Beam) * (discretiza - Extremos_Discretiza_Beam)

            elif discretiza <= Extremos_Discretiza_Beam + Internos_Discretiza_Beam + Mid_discretiza_Beam:
                # Centro
                x = x_ini + length_ext + length_int + (length_mid / Mid_discretiza_Beam) * (discretiza - Extremos_Discretiza_Beam - Internos_Discretiza_Beam)

            elif discretiza <= Extremos_Discretiza_Beam + Internos_Discretiza_Beam * 2 + Mid_discretiza_Beam:
                # Interna derecha
                x = x_ini + length_ext + length_int + length_mid + (length_int / Internos_Discretiza_Beam) * (discretiza - Extremos_Discretiza_Beam - Internos_Discretiza_Beam - Mid_discretiza_Beam)

            else:
                # Extremo derecho
                x = x_ini + length_ext + length_int + length_mid + length_int + (length_ext / Extremos_Discretiza_Beam) * (discretiza - Extremos_Discretiza_Beam - 2 * Internos_Discretiza_Beam - Mid_discretiza_Beam)

            nodeTag = int(str(pav) + str(0) + str(tramox) + str(0) + str(1) + str(discretiza))
            ops.node(nodeTag, x, y_coord)

        # === CREACIÓN DE ELEMENTOS DE VIGA ===
        # Recuperar la configuración de secciones para esta viga específica
        _config = beam_section_config[(pav, tramox)]

        for discretiza in range(1, total_elements_beam + 1):
            if discretiza == 1:
                nodo_i = int(str(pav) + str(0) + str(tramox))
                nodo_j = int(str(pav) + str(0) + str(tramox) + str(0) + str(1) + str(discretiza))
            elif discretiza == total_elements_beam:
                nodo_i = int(str(pav) + str(0) + str(tramox) + str(0) + str(1) + str(discretiza - 1))
                nodo_j = int(str(pav) + str(0) + str(tramox + 1))
            else:
                nodo_i = int(str(pav) + str(0) + str(tramox) + str(0) + str(1) + str(discretiza - 1))
                nodo_j = int(str(pav) + str(0) + str(tramox) + str(0) + str(1) + str(discretiza))

            # Asignación de integración según zona (leída desde beam_section_config)
            if discretiza <= Extremos_Discretiza_Beam:
                integraTag = _config['ext_izq']
            elif discretiza <= Extremos_Discretiza_Beam + Internos_Discretiza_Beam:
                integraTag = _config['int_izq']
            elif discretiza <= Extremos_Discretiza_Beam + Internos_Discretiza_Beam + Mid_discretiza_Beam:
                integraTag = _config['mid']
            elif discretiza <= Extremos_Discretiza_Beam + 2 * Internos_Discretiza_Beam + Mid_discretiza_Beam:
                integraTag = _config['int_der']
            else:
                integraTag = _config['ext_der']

            eleTag = int(str(pav) + str(0) + str(tramox) + str(0) + str(0) + str(1) + str(discretiza))

            if Formulation == 'dispBeamColumn':
                ops.element(Formulation, eleTag, nodo_i, nodo_j, BeamTransfTag, integraTag)
            else:
                ops.element(Formulation, eleTag, nodo_i, nodo_j, BeamTransfTag, integraTag, 'iter', maxIter, tol)

            eleBeam_section_map[eleTag] = integraTag



  

# =============================================================================
#                    Engastamento Perfeito na base dos Pilares                 
# =============================================================================
    
ops.fixY(0.0, 1, 1, 1) 


# opsv.plot_model(element_labels=0, node_labels=0)
# opsv.plot_model(element_labels=1, node_labels=1)


# =============================================================================
#                  Organizando Matriz de Nós                       
# =============================================================================

# Organizando os Nós em uma Matriz
nome_nos = ops.getNodeTags()
matriz_nos = np.zeros([len(nome_nos), 3])

ii = 0
for no in nome_nos:
    matriz_nos[ii,0] = no
    matriz_nos[ii,1] = ops.nodeCoord(no, 1)
    matriz_nos[ii,2] = ops.nodeCoord(no, 2)
    ii += 1


# =============================================================================
#              Organizando Matriz de Elementos e Plotando o Modelo             
# =============================================================================

# Organizando os Elementos em uma Matriz
nome_elementos = ops.getEleTags()
matriz_elementos = np.zeros([len(nome_elementos), 5])


ii = 0
for eleTag in nome_elementos:
    no_i = ops.eleNodes(eleTag)[0]
    no_j = ops.eleNodes(eleTag)[1]
    matriz_elementos[ii,0] = eleTag
    matriz_elementos[ii,1] = ops.nodeCoord(no_i, 1)    
    matriz_elementos[ii,2] = ops.nodeCoord(no_i, 2)
    matriz_elementos[ii,3] = ops.nodeCoord(no_j, 1)
    matriz_elementos[ii,4] = ops.nodeCoord(no_j, 2)

    # ax.plot([matriz_elementos[ii,1], matriz_elementos[ii,3]], [matriz_elementos[ii,2], matriz_elementos[ii,4]], color='mediumblue')
    ii +=1


for no in nome_nos:
    if len(str(no)) == 3 or len(str(no)) == 4:
        if str(no)[0] == '1' and len(str(no)) == 3:
            no_i = ops.nodeCoord(no, 1)
            no_j = ops.nodeCoord(no, 2)
            #ax.scatter(no_i, no_j, marker='X', color='black')
        else:
            no_i = ops.nodeCoord(no, 1)
            no_j = ops.nodeCoord(no, 2)
            #ax.scatter(no_i, no_j, marker='o', color='darkred')
  
# plt.figure()
# plt.show()

print('Geomtry definided')
   