########################################
# LOADS
########################################

# Brazilian Standard ABNT NBR 6120-2019
density_concrete = 2500 # Density of concrete [kg/m³] for calculating the self-weight of beams, columns, and slabs
# qSlab_SW = 0.10 * density_concrete * 9.81 # Slab Self-Weight (SW) [N/m²]. Assuming slab thickness (esp) = 10 cm.  - tirar 
# qSlab_SDL = 1.50 * 1000   # [N/m²] Superimposed Dead Load (SDL) = 1.50 kN/m²
# qSlab_LL = 1.50 * 1000 # [N/m²] Live Load (LL) = 1.50 kN/m²
qSlabs = 0.0
#qSlab_SW + qSlab_SDL + 0.25 * (qSlab_LL) # Combination load for slabs [N/m²] (1.0 DL + 0.25 LL).
# qBeams_InfillWall = 1.6 * 2.60 * 1000 # Infill wall load [N/m] = 1.6 kN/m² * 2.60 m height.



# matriz_elementos is defined in Geometry.py
# matriz_elementos has the following structure:

# column zero: tags of the elements
# column one: x-coordinate of the initial node of the element
# column two: y-coordinate of the initisl node of the element
# column three: x-coordinate of the final node of the element
# column four: y-coordinate of the final node of the element


if __name__ == "__main__":

    qVigas_Pp = b_beam*h_beam*density_concrete*9.81 #N/m  2500 pueedo referenciar con la normativa chinesa Cargas-GB-50009-2012-EN - Tabla A Item 6 Reinforced Concrete 24 - 25 kN/m3 
    # qVigas_Pp = 0


    tag_pattern = 1                                  
    tag_timeseries = 1

    # ops.recorder('Node', "-file", "./deletar.out", "-time", "-node", 1011, "-dof",1, 2, 3, 'reaction')

    # Aplicando cargas gravitacionais
    # Create a Plain load pattern with a Linear TimeSeries
    ops.timeSeries('Linear', tag_timeseries)

    #pattern('Plain', patternTag, tsTag, '-fact', fact)
    ops.pattern('Plain', tag_pattern, tag_timeseries)


    for info_elemento in matriz_elementos:
        elemento = str(int(info_elemento[0]))   # A tag string is taken from the element
        if len(elemento) == 7:
            if elemento[-2] == '1': # It is used to separate beams from columns. '1' represents a beam and '2' represents a column. For exmaple: 30200'1'1
                no1_vao = int(elemento[0:-4]) # Returns the tag of the initial node of the beam (the first three digits of the element tag) Example = 3020011 (beam tag) then no1_vao = 302
                no2_vao = int(no1_vao) + 1 # Returns the tag of the final node of the beam. Example = 3020011 (beam tag) then no2_vao = 303
                Vao_L = ops.nodeCoord(no2_vao, 1) - ops.nodeCoord(no1_vao,1) # Calculates the beam length.
                
                # q_Viga = round(Factor_Incremento*qVigas_Pp)
                q_Viga = round(qVigas_Pp + qSlabs*Vao_L/4)
                ops.eleLoad('-ele', int(elemento), '-type', '-beamUniform', -q_Viga)
                print(f'Viga: {elemento}, com carga: {q_Viga}')

                # Pil_mass_esq = round((q_Viga * Vao_L/(Extremos_Discretiza_Beam*2+Internos_Discretiza_Beam*2+Mid_discretiza_Beam) / 2)/9.81, 2)
                # Pil_mass_dir = round((q_Viga * Vao_L/(Extremos_Discretiza_Beam*2+Internos_Discretiza_Beam*2+Mid_discretiza_Beam) / 2)/9.81, 2)
            
                # indice_no_esq = nos_pilares.index(no1_vao)
                # indice_no_dir = nos_pilares.index(no2_vao)
                
                # massa_pil[indice_no_esq][1] += Pil_mass_esq
                # massa_pil[indice_no_dir][1] += Pil_mass_dir         
            
                
            if elemento[-2] == '2': # It is used to separate beams from columns. '1' represents a beam and '2' represents a column. For exmaple: 30200'2'1
                q_Pil = b_col * h_col * density_concrete*9.81
                ops.eleLoad('-ele', int(elemento), '-type', '-beamUniform', 0, -q_Pil)
                print(f'Pilar: {elemento}, com carga: {q_Pil}')
                
            




        # if len(elemento) == 8:
        #     if elemento[-3] == '1': # It is used to separate beams from columns. '1' represents a beam and '2' represents a column. For exmaple: 30200'1'1
        #         no1_vao = int(elemento[0:-5]) # Returns the tag of the initial node of the beam (the first three digits of the element tag) Example = 3020011 (beam tag) then no1_vao = 302
        #         no2_vao = int(no1_vao) + 1 # Returns the tag of the final node of the beam. Example = 3020011 (beam tag) then no2_vao = 303
        #         Vao_L = ops.nodeCoord(no2_vao, 1) - ops.nodeCoord(no1_vao,1) # Calculates the beam length.
                
        #         q_Viga = round(Factor_Incremento*qVigas_Pp)
        #         ops.eleLoad('-ele', int(elemento), '-type', '-beamUniform', -q_Viga)



        #         if elemento[0] == '2':
        #         #Carga de las paredes de mamposteria: Se coloca sólo en las vigas inferiores
        #             q_Viga_Alv = round(Factor_Incremento*qVigas_Alv)     
        #             ops.eleLoad('-ele', int(elemento), '-type', '-beamUniform', -q_Viga_Alv)  



        #         # print(f'Viga: {elemento}, com carga: {q_Viga}')
                
                
        #         # Pil_mass_esq = round((q_Viga * Vao_L/Beam_discretiza / 2)/9.81, 2)
        #         # Pil_mass_dir = round((q_Viga * Vao_L/Beam_discretiza / 2)/9.81, 2)
                
        #         # indice_no_esq = nos_pilares.index(no1_vao)
        #         # indice_no_dir = nos_pilares.index(no2_vao)
                
        #         # massa_pil[indice_no_esq][1] += Pil_mass_esq
        #         # massa_pil[indice_no_dir][1] += Pil_mass_dir
                
            


        #     if elemento[-3] == '2': # It is used to separate beams from columns. '1' represents a beam and '2' represents a column. For exmaple: 30200'2'1
                
        #         q_Pil = Factor_Incremento*(b_col * h_col * 2400*9.81)
        #         # q_Pil = 0
        #         ops.eleLoad('-ele', int(elemento), '-type', '-beamUniform', 0, -q_Pil)
        #         # print(f'Pilar: {elemento}, com carga: {q_Pil}')
        #         # opsv.plot_loads_2d()



    print('Carga vertical Definida')


#Carga concentrada
timeSeriesTag = 10
patternTag = 10
P_axial_1 = 400 #kN
P_axial_2 = 400 #kN
ops.timeSeries('Linear', timeSeriesTag)
ops.pattern('Plain', patternTag, timeSeriesTag)

ops.load(101, 0, P_axial_1, 0)
ops.load(101, 0, P_axial_2, 0)

ops.constraints('Plain')
ops.numberer('RCM')
ops.system('BandGeneral')
ops.test('NormDispIncr', 1e-5, 10)
ops.algorithm('Newton')

nSteps = 10
dt = 1/nSteps
ops.integrator('LoadControl', dt)
ops.analysis('Static')
ok = ops.analyze(nSteps)
if (ok == 0):
    print('Carga axial ok')
else:
    print('Carga axial falhou')

ops.loadConst('-time', 0.0)










