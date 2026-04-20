# Mass in beams and columns

# Import vertical Loads defined in CargaVertical.py to calculate the mass matrix

# -----------------------------------------------------------------------
# Concentrated mass in the nodes of the beams
# -----------------------------------------------------------------------

qVigas_Pp = b_beam*h_beam*density_concrete*9.81 #N/m  2500 pueedo referenciar con la normativa chinesa Cargas-GB-50009-2012-EN - Tabla A Item 6 Reinforced Concrete 24 - 25 kN/m3 
    # qVigas_Pp = 0


# nome_nos definido en Geometry.py
nos_pilares = []  # List to store the tags of the initial and end nodes of the beams and columns (Intersection nodes)
massa_pil = []  # Save a matrix with the intersection nodes tags and their masses [node_tag, mass_value=0]. The mass will be calculated later
for no in nome_nos:  # nome_nos is the tag list of all nodes. Nome_nos is defined in CargaVertical.py
    if len(str(no)) == 3 or len(str(no)) == 4:
        nos_pilares.append(no)
        aux = [no, 0]
        massa_pil.append(aux)

for info_elemento in matriz_elementos:
        elemento = str(int(info_elemento[0]))   # A tag string is taken from the element
        if len(elemento) == 7:
            if elemento[-2] == '1': # It is used to separate beams from columns. '1' represents a beam and '2' represents a column. For exmaple: 30200'1'1
                no1_vao = int(elemento[0:-4]) # Returns the tag of the initial node of the beam (the first three digits of the element tag) Example = 3020011 (beam tag) then no1_vao = 302
                no2_vao = int(no1_vao) + 1 # Returns the tag of the final node of the beam. Example = 3020011 (beam tag) then no2_vao = 303
                Vao_L = ops.nodeCoord(no2_vao, 1) - ops.nodeCoord(no1_vao,1) # Calculates the beam length.
                
                # q_Viga = round(Factor_Incremento*qVigas_Pp)
                q_Viga = round(qVigas_Pp + qSlabs*Vao_L/4)

                Pil_mass_esq = round((q_Viga * Vao_L/(Extremos_Discretiza_Beam*2+Internos_Discretiza_Beam*2+Mid_discretiza_Beam) / 2)/9.81, 2)
                Pil_mass_dir = round((q_Viga * Vao_L/(Extremos_Discretiza_Beam*2+Internos_Discretiza_Beam*2+Mid_discretiza_Beam) / 2)/9.81, 2)
            
                indice_no_esq = nos_pilares.index(no1_vao)
                indice_no_dir = nos_pilares.index(no2_vao)
                
                massa_pil[indice_no_esq][1] += Pil_mass_esq
                massa_pil[indice_no_dir][1] += Pil_mass_dir         
            


print("This is the mass matrix of the beams:", massa_pil)


# Concentrated mass in the nodes of the columns of each floor


# -----------------------------------------------------------------------
# Concentrated mass in the nodes of the columns
# -----------------------------------------------------------------------


# Inserindo as Massas concentradas nos nós dos pilares ao nível dos pavimentos
massPav = [0] * num_pav   # The variable num_pav considers the ground floor
SomaProdutoMassasX = [0] * num_pav 
SomaProdutoMassasY = [0] * num_pav
nos_base = []

for pilar in nos_pilares:  # 
    pav = int(str(pilar)[0:-2])
    if pav != 1:
        L_pilar = Z_pavs[pav-1] - Z_pavs[pav-2]  # Length of the column
        elemento = int(str(pav-1) + str(pilar)[-2:]+str(0)+str(0)+str(2)+str(1))
        Pil_mass_pp = b_col *h_col*L_pilar*density_concrete
        
        indice_pilar = nos_pilares.index(pilar)
        massa_pil[indice_pilar][1] += Pil_mass_pp
        ops.mass(massa_pil[indice_pilar][0], massa_pil[indice_pilar][1], massa_pil[indice_pilar][1])
        print(massa_pil[indice_pilar][0], ' massa:', massa_pil[indice_pilar][1]) 


        # Obtendo a Massa dos Pavimentos
        SomaProdutoMassasX[pav-1] += massa_pil[indice_pilar][1] * ops.nodeCoord(massa_pil[indice_pilar][0], 1) 
        
        massPav[pav-1] += massa_pil[indice_pilar][1]
        
    else:
        nos_base.append(pilar)

m = 1000.0  # kg (valor qualquer só pra testar)

ops.mass(101, m, m, 1e-9)
ops.mass(102, m, m, 1e-9)
ops.mass(201, m, m, 1e-9)
ops.mass(202, m, m, 1e-9)

print("This is the mass matrix, including the columns mass:", massa_pil)