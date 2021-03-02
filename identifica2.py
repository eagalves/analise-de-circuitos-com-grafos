#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 15:59:28 2019

@author: fred/evandro
"""

from collections import namedtuple
import networkx as nx
import networkx.algorithms.isomorphism as iso
import matplotlib.pyplot as plot
import numpy as np



#lista de especificações de simplificações
# CP - capacitores em paralelo
# CS - capacitores em série
# RP - reistores em paralelo
# RS - resistores em série

list_espec_simpl = ['CP', 'CS', 'RP', 'RS']


trans_data = namedtuple('transistor_data',['trans_name', 'drain', 'gate', 'source','bulk','typeT','L','W'])
cap_data = namedtuple('capacitor_data',['cap_name', 'pin1', 'pin2', 'C'])
res_data = namedtuple('resistor_data',['res_name', 'pin1', 'pin2', 'R'])


plotar = 0 # 1 plotar / 0 não plotar


def read_log(fp):
    arch = []
    for line in fp:
        if line[0] == 'C' and line[1] =='M':
            arch.append(line[9])
    return(arch)
    

def read_netlist(fp):
    """ Reads netlist file """
    trans_all = []
    cap_all = []
    res_all = []
    for line in fp:
        if line[0] == 'C': #capacitor
             line = line.replace('(', '')
             line = line.replace(')', '')
             line = line.replace('C=', '')
             line2 = line.split()
             cap = cap_data(cap_name=line2[0],
             pin1=line2[1],
             pin2=line2[2],
             C=line2[3])
             cap_all.append(cap)

        if line[0] == 'T': #transistor
             line = line.replace('(', '')
             line = line.replace(')', '')            
             line = line.replace('L=', '')
             line = line.replace('W=', '')
             line2 = line.split()
             trans = trans_data(trans_name=line2[0],
             drain=line2[1],
             gate=line2[2],
             source=line2[3],
             bulk = line2[4],
             typeT = line2[5],
             L = line2[6],
             W = line2[7])
             trans_all.append(trans)
        if line[0] == 'R': #transistor
             line = line.replace('(', '')
             line = line.replace(')', '')            
             line = line.replace('R=', '')
             line2 = line.split()
             res = res_data(res_name=line2[0],
             pin1=line2[1],
             pin2=line2[2],
             R=line2[3])
             res_all.append(res)

       
    return(trans_all,cap_all,res_all)


def read_arch(arq,arch_list): #carregar arquiteturas
    T_netlist,C_netlist,R_netlist = read_netlist(open(arq).readlines())
    arch_list.append([T_netlist,C_netlist,R_netlist])

    return(arch_list)




def create_graph(T_netlist,R_netlist,C_netlist,W,P):
    #W - flag to create weighted graphs
    #P - flag - True to plot
    """ Represent netlist using graph structure"""
    graph = nx.Graph()
    #graph = nx.MultiGraph()
    color_map = []
    W = True
    P = False
    if W == True:
    
        for tran in T_netlist:
            color_map.append('k')
            graph.add_edges_from([(tran.trans_name, tran.drain, {'weight':1,'color':'deepskyblue'}), 
                                  (tran.trans_name, tran.gate, {'weight':2,'color':'b'}), 
                                  (tran.trans_name, tran.source, {'weight':3,'color':'darkblue'})])
            graph.nodes[tran.trans_name]['type']='T'
            #graph.node[tran.trans_name]['valsub']='NV'  # indica se o nó é valido para comparação de isomorphismo (NV = nó valido para subgrafo)
            #graph.node[tran.drain]['valsub']='NV'
            #graph.node[tran.gate]['valsub']='NV'
            #graph.node[tran.source]['valsub']='NV'
            graph.nodes[tran.trans_name]['L']=float(tran.L)
            graph.nodes[tran.trans_name]['W']=float(tran.W)
            
        for tran in R_netlist:
            color_map.append('k')
            graph.add_edges_from([(tran.res_name, tran.pin1, {'weight':4,'color':'r'}), 
                                  (tran.res_name, tran.pin2, {'weight':4,'color':'r'})])
            graph.nodes[tran.res_name]['type']='R'
            #graph.node[tran.res_name]['valsub']='NV'  # indica se o nó é valido para comparação de isomorphismo (NV = nó valido para subgrafo)
            #graph.node[tran.pin1]['valsub']='NV'
            #graph.node[tran.pin2]['valsub']='NV'
            graph.nodes[tran.res_name]['R']=float(tran.R)
            
        for tran in C_netlist:
            color_map.append('k')
            graph.add_edges_from([(tran.cap_name, tran.pin1, {'weight':5,'color':'g'}), 
                                  (tran.cap_name, tran.pin2, {'weight':5,'color':'g'})])
            graph.nodes[tran.cap_name]['type']='C'
            #graph.node[tran.pin1]['valsub']='NV'
            #graph.node[tran.pin2]['valsub']='NV'
            #graph.node[tran.cap_name]['valsub']='NV'  # indica se o nó é valido para comparação de isomorphismo (NV = nó valido para subgrafo)
            graph.nodes[tran.cap_name]['C']=float(tran.C)
            
    else: ## CASO EU NAO QUISER COLOCAR "PESO" PARA OS NÓS
        for tran in T_netlist:
            color_map.append('k')
            graph.add_edges_from([(tran.trans_name, tran.drain), 
                                  (tran.trans_name, tran.gate), 
                                  (tran.trans_name, tran.source)])
        for tran in R_netlist:
            color_map.append('k')
            graph.add_edges_from([(tran.res_name, tran.pin1), 
                                  (tran.res_name, tran.pin2)])
    
        for tran in C_netlist:
            color_map.append('k')
            graph.add_edges_from([(tran.cap_name, tran.pin1), 
                                  (tran.cap_name, tran.pin2)])
    if P == True:
        edges = graph.edges()    
        colors = [graph[u][v]['color'] for u,v in edges]
        nx.draw(graph, with_labels=True,node_color=color_map, edge_color=colors, node_size=15, font_size = 8,figsize=(40,40)) 
        plot.show() # To plot graphs

    return(graph)
    
    
def plot_graph(graph): # para plotar os grafos ou parte deles    

    edges = graph.edges()    
    colors = [graph[u][v]['color'] for u,v in edges]
    nx.draw(graph, with_labels=True, edge_color=colors, node_size=40, font_size = 20,figsize=(35,35)) #30 8
    #labels = nx.get_edge_attributes(graph,'weight')
    #pos=nx.get_node_attributes(graph,'pos')
    #nx.draw_networkx_edge_labels(graph,pos,edge_labels=labels)
    plot.show() # To plot graphs
  
    
    

def simplificar(graph,NA,NB,NC,NE1,NE2,tipo):
    
    if tipo == 'CS':
        graph.add_edges_from([(NE1 + '_' + NE2, NA, {'weight':5,'color':'g'}), 
                              (NE1 + '_' + NE2, NC, {'weight':5,'color':'g'})])
        graph.nodes[NE1 + '_' + NE2]['type']='C'
        graph.nodes[NE1 + '_' + NE2]['valsub']='NV'  # indica se o nó é valido para comparação de isomorphismo (NV = nó valido para subgrafo)
        #graph.node[NA]['valsub']='NV'
        #graph.node[NC]['valsub']='NV'
        graph.nodes[NE1 + '_' + NE2]['C']= 1/((1/graph.nodes[NE1]['C'])+(1/graph.nodes[NE2]['C']))
        
        graph.remove_node(NE1)
        graph.remove_node(NE2)
    

    if tipo == 'RS':
        graph.add_edges_from([(NE1 + '_' + NE2, NA, {'weight':4,'color':'r'}), 
                              (NE1 + '_' + NE2, NC, {'weight':4,'color':'r'})])
        graph.nodes[NE1 + '_' + NE2]['type']='R'
        #graph.node[NE1 + '_' + NE2]['valsub']='NV'  # indica se o nó é valido para comparação de isomorphismo (NV = nó valido para subgrafo)
        graph.nodes[NE1 + '_' + NE2]['R']= graph.nodes[NE1]['R']+graph.nodes[NE2]['R']
        
        graph.remove_node(NE1)
        graph.remove_node(NE2)
    
    if tipo == 'CP':
        graph.add_edges_from([(NE1 + '//' + NE2, NA, {'weight':5,'color':'g'}), 
                              (NE1 + '//' + NE2, NB, {'weight':5,'color':'g'})])
        graph.nodes[NE1 + '//' + NE2]['type']='C'
        #graph.node[NE1 + '//' + NE2]['valsub']='NV'  # indica se o nó é valido para comparação de isomorphismo (NV = nó valido para subgrafo)
        graph.nodes[NE1 + '//' + NE2]['C']= graph.nodes[NE1]['C']+graph.nodes[NE2]['C']
        
        graph.remove_node(NE1)
        graph.remove_node(NE2)

    if tipo == 'RP':
        graph.add_edges_from([(NE1 + '//' + NE2, NA, {'weight':4,'color':'r'}), 
                              (NE1 + '//' + NE2, NB, {'weight':4,'color':'r'})])
        graph.nodes[NE1 + '//' + NE2]['type']='R'
        #graph.node[NE1 + '//' + NE2]['valsub']='NV'  # indica se o nó é valido para comparação de isomorphismo (NV = nó valido para subgrafo)
        graph.nodes[NE1 + '//' + NE2]['R']= 1/((1/graph.nodes[NE1]['R'])+(1/graph.nodes[NE2]['R']))
        
        graph.remove_node(NE1)
        graph.remove_node(NE2)
    
    return(graph)

    
    
def main():
    """ Main func """
    #caminho dos circuitos
    pathC = 'netlists/script/experimento1/circuits/' 
    
    
    
    #arquivo de simplificações de circuito
    list_simpl = []
    for i in range(1,5):
        list_simpl.append('netlists/archSimpl/simplifica' + str(i) + '.sp')
    #list_simpl. é uma variavel que recebe o caminho com as simplificações
    
    list_arq = []
    for i in range(1,6):
        list_arq.append('netlists/script/experimento1/CM_circuits/cm' + str(i) + '.sp')
        

        
#        ['netlists/script/CM_circuits/cm0.sp','netlists/script/CM_circuits/cm1.sp','netlists/script/CM_circuits/cm2.sp',
#              'netlists/script/CM_circuits/cm3.sp','netlists/script/CM_circuits/cm4.sp','netlists/script/CM_circuits/cm5.sp',
#              'netlists/script/CM_circuits/cm6.sp','netlists/script/CM_circuits/cm7.sp','netlists/script/CM_circuits/cm8.sp',
#              'netlists/script/CM_circuits/cm9.sp','netlists/script/CM_circuits/cm10.sp','netlists/script/CM_circuits/cm10.sp']
#    

#########################################################################
    #carrega arquiteturas para simplificação de circuitos (associação de resistores e capacitores)
    archSimpl_list = []
    for arq in list_simpl:  
        archSimpl_list = read_arch(arq,archSimpl_list)
# archSimpl_list recebe as arquiteturas dentro do caminho especificado(list_simpl), exemplo
# para a primeira posição deste vetor
# C1 (NA NB) C=1.0E-7
# C2 (NA NB) C=1.0E-7
#########################################################################
# carrega arquiteturas espelhos de corrente # que sao os cm1,cm2,...
    arch_list = []
    for arq in list_arq:
        arch_list = read_arch(arq,arch_list) # read_netlist está dentro da função read_arch
#exemplo da primeira posição do vetor:
# T73 ( net23 net23 0 0)  nfet  L=9.64E-6 W=1.12E-6
# T74 ( net1 net23 0 0)  nfet  L=9.64E-6 W=1.12E-6
# R75 ( net1 net22)  R=4.0E3
#########################################################################
        
    #carrega circuito
    listaMatchCircs = []
    listaMatchCircsReal = []
    contador = 0
    tot = 5# total 
    acc = np.zeros(5)
    #T_netlist,C_netlist,R_netlist = read_netlist(open('netlists/script/circuits/rcircuit0teste2.sp').readlines())
    #T_netlist,C_netlist,R_netlist = read_netlist(open('netlists/script/teste/simplifica/rcircuit0.sp').readlines())
    
    
    
    
    for circ in range(2,3):
        T_netlist,C_netlist,R_netlist = read_netlist(open(pathC + 'rcircuit' + str(circ) + '.sp').readlines())
        arch_in_circ = read_log(open(pathC + 'rcircuit' + str(circ) + '.log').readlines())
        
        
        #cria grafo do circuito sem peso
        #graph = create_graph(T_netlist,R_netlist,C_netlist, False)
    
        #Cria grafo do circuito com pesos
        graph = create_graph(T_netlist,R_netlist,C_netlist,True,False) 
    
        
        nx.draw(graph, with_labels=True, node_size=10, font_size = 6,figsize=(400,400)) 
        nx.draw_spectral(graph, with_labels=True, node_size=10, font_size = 6) 
        nx.draw_spring(graph, with_labels=True, node_size=10, font_size = 8)     
        nx.draw_circular(graph, with_labels=True) 



        # #realiza passagens pelo circuitos para identificar e realizar possíveis simplificações 
        sair = 0
        nCS = 0 #numero de Capacitores em série
        nCP = 0 #numero de Capacitores em paralelo
        nRS = 0 #numero de Resistores em série
        nRP = 0 #numero de Resistores em paralelo
  
######################################## SIMPLIFICAÇÃO ##########################################
#################################################################################################
      
        while sair == 0:
            sair = 1 # se ele fizer qualquer simplificação ele muda este flag para 0 e verifica novamente
            cont_archSimpl = -1
            for arch in archSimpl_list:
                cont_archSimpl=cont_archSimpl +1
                #cria um grafo da arquitetura que se quer simplificar para comparar por ismorfismo
                graph_arch = create_graph(arch[0],arch[2],arch[1],True,False)
                # em <- funcao customizada de edge_match
                em = iso.numerical_edge_match(['weight','weight','weight','weight','weight'], [1,2,3,4,5])
                # nm <- funcao customizada de node match
                nm = iso.categorical_node_match(['type', 'type'], ['C','R'])
                GM = iso.GraphMatcher(graph,graph_arch,edge_match=em,node_match=nm)
                II = GM.subgraph_is_isomorphic() # retorna TRUE or FALSE
                
              
                print('simplificacao: ',cont_archSimpl+1,II) #+1 porque as arquiteturas começam em 1 e não zero
                
                
                if II: #apenas para visualização 
                    #if plotar == 1:
                    for subgraph in GM.subgraph_isomorphisms_iter():
                        print(subgraph)
                        plot_graph(graph.subgraph(subgraph.keys()))
                            
                                        
                    
                lista_subgraph = []
                for subgraph in GM.subgraph_isomorphisms_iter(): 
                    lista_subgraph.append(subgraph)

                #verifica condições extras para simplificação
                #  - capacitores e resistores em série não podem ter mais que duas arestas no nó central entre eles
                
                if list_espec_simpl[cont_archSimpl] == 'CS': #para capacitores em série
                    for subgraph in lista_subgraph:
                     
                        #busca estrutura no grafo do circuito
                        NA = list(subgraph.keys())[list(subgraph.values()).index('NA')]
                        NB = list(subgraph.keys())[list(subgraph.values()).index('NB')]
                        NC = list(subgraph.keys())[list(subgraph.values()).index('NC')]
                        NE1 = list(subgraph.keys())[list(subgraph.values()).index('C1')] #nó elemento (pode ser C ou R)
                        NE2 = list(subgraph.keys())[list(subgraph.values()).index('C2')] #nó elemento (pode ser C ou R)
                        #verifica número de conexões no nó central dos capcitores e se o nó existe (se já não foi simplificado)
                        if (graph.has_node(NE1)) and (graph.has_node(NE2)): # existem os nós (não foram simplificados ainda)
                            if (len(graph.edges(NB))== 2): #pode simplificar
                                nCS = nCS + 1
                                graph = simplificar(graph,NA,NB,NC,NE1,NE2,'CS') # função de simplificação
                                sair = 0
                            #else:
                                #graph.node[NB]['valsub']='NNV'  # indica se o nó é valido para comparação de isomorphismo (NNV = nó Não valido para subgrafo - tem mais de duas conexções no nó intermediário)    

                if list_espec_simpl[cont_archSimpl] == 'RS': #para resistores em série
                    for subgraph in lista_subgraph:
                        #busca estrutura no grafo do circuito
                        NA = list(subgraph.keys())[list(subgraph.values()).index('NA')]
                        NB = list(subgraph.keys())[list(subgraph.values()).index('NB')]
                        NC = list(subgraph.keys())[list(subgraph.values()).index('NC')]
                        NE1 = list(subgraph.keys())[list(subgraph.values()).index('R1')] #nó elemento (pode ser C ou R)
                        NE2 = list(subgraph.keys())[list(subgraph.values()).index('R2')] #nó elemento (pode ser C ou R)
                        #verifica número de conexões no nó central dos resistores e se o nó existe (se já não foi simplificado)
                        if (len(graph.edges(NB))== 2) and (graph.has_node(NE1)) and (graph.has_node(NE2)): #pode simplificar
                            nRS = nRS + 1
                            graph = simplificar(graph,NA,NB,NC,NE1,NE2,'RS')
                            sair = 0
                            
                if list_espec_simpl[cont_archSimpl] == 'CP': #para capacitores em paralelo
                    #cont = 0
                    for subgraph in lista_subgraph:
                        # AUX DEBUG #######################
                        #if cont == 1:
                        #    print('break ',cont)
                        #    break
                        #print('cont ',cont)
                        #cont = cont + 1
                        #print(list(subgraph.keys())[list(subgraph.values()).index('C1')], list(subgraph.keys())[list(subgraph.values()).index('C2')], '\n')
                        #############################
                        
                        #busca estrutura no grafo do circuito
                        NA = list(subgraph.keys())[list(subgraph.values()).index('NA')]
                        NB = list(subgraph.keys())[list(subgraph.values()).index('NB')]
                        NC = 'none'
                        NE1 = list(subgraph.keys())[list(subgraph.values()).index('C1')] #nó elemento (pode ser C ou R)
                        NE2 = list(subgraph.keys())[list(subgraph.values()).index('C2')] #nó elemento (pode ser C ou R)
                        #verifica se o nó existe (se já não foi simplificado)
                        if (graph.has_node(NE1)) and (graph.has_node(NE2)): #pode simplificar
                            nCP = nCP + 1
                            graph = simplificar(graph,NA,NB,NC,NE1,NE2,'CP')
                            sair = 0

                if list_espec_simpl[cont_archSimpl] == 'RP': #para resistores em paralelo
                    for subgraph in lista_subgraph:
                        #busca estrutura no grafo do circuito
                        NA = list(subgraph.keys())[list(subgraph.values()).index('NA')]
                        NB = list(subgraph.keys())[list(subgraph.values()).index('NB')]
                        NC = 'none'
                        NE1 = list(subgraph.keys())[list(subgraph.values()).index('R1')] #nó elemento (pode ser C ou R)
                        NE2 = list(subgraph.keys())[list(subgraph.values()).index('R2')] #nó elemento (pode ser C ou R)
                        #verifica se o nó existe (se já não foi simplificado)
                        if (graph.has_node(NE1)) and (graph.has_node(NE2)): #pode simplificar
                            nRP = nRP + 1
                            graph = simplificar(graph,NA,NB,NC,NE1,NE2,'RP')
                            sair = 0
        
###########################################################################################################
###########################################################################################################


    
        #cria grafo das arquiteturas
        cont_arch = -1
        listaMatch =[]
        for arch in arch_list:
            cont_arch=cont_arch +1
            #sem peso
            #graph_arch = create_graph(arch[0],arch[2],arch[1], False)
            #COm peso
            graph_arch = create_graph(arch[0],arch[2],arch[1],True,False)
    
            #para encontrar isomorfismo em grafo sem peso                
            #GM = iso.GraphMatcher(graph,graph_arch)
    
            #em = iso.numerical_multiedge_match(['weight','weight','weight'], [1,2,3])
            em = iso.numerical_edge_match(['weight','weight','weight','weight','weight'], [1,2,3,4,5])
            #em = iso.numerical_edge_match('weight', 2)
            GM = iso.GraphMatcher(graph,graph_arch,edge_match=em)
            II = GM.subgraph_is_isomorphic()
            #print(GM.is_isomorphic())
            print('espelho de corrente: ',cont_arch+1,II) #+1 porque as arquiteturas começam em 1 e não zero
            
            
            
            #para teste 
            if II:
               listaMatch.append(str(cont_arch+1))
               for subgraph in GM.subgraph_isomorphisms_iter():
                   print(subgraph)
                   
                   plot_graph(graph.subgraph(subgraph.keys()))
        
        
        # resultados acurácia
        print('nCS,nCP,nRS,nRP', nCS,nCP,nRS,nRP)
        
        
        listaMatchCircs.append(listaMatch)
        listaMatchCircsReal.append(arch_in_circ)
        a=set(listaMatch)
        b=set(arch_in_circ)
        contador = contador+1
        print('contador =', contador)
        acc[circ] = len(a.intersection(b))
        tot = tot + len(b)
        print(' ___________________________________________________________' )
        print(' ___________________________________________________________' )
   
    
        print('Acurácia = ' + str(sum(acc)/tot))

#plot_graph(graph.subgraph({'T398': 'T73', 'net26': 'net23', 'vdd!': '0', 'T399': 'T74', 'net8': 'net1', 'R182': 'R75', 'net19': 'net22'}.keys()))
if __name__ == '__main__':
    main()


#The next lines plots the graphs fro netlists using matplotlib:
