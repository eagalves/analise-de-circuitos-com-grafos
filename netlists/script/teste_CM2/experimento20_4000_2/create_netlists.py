# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 19:57:04 2021

@author: Vandinho
"""


#!/usr/bin/python
# -*- coding: utf-8 -*-

# Script that creates random circuit netlists 
# can also include CMs

#### TODOs
# date: 12/02/2019
# ** general
# - more elements (real R,C)
# - MOS parameters
# - removal of floating nets
# ***CMs
# - Elements in CMs not only consecutive
# - Sizing in CMs (now, all FETs w/ same size
# - more CM_architectures
# - elements of CMs in nelists more distributed

# Version 1.2 (25/03/2019)
# - added option CM_type
# - fixed randomization of CM insertion

# Version 1.1 (15/02/2019)
# - No R or C element can have pins w/ same nets
# - log files contain netlist of added CMs in netlist

import argparse
import os
import sys
import pdb
import random
import numpy as np

############## initial definitions   ##############

# max. relation between nets and elements, 
# e.g. 80: max. number of nets is 80% of number of circuit elements
NETS_VS_ELEMENTS = 0.8

# probility that a net is VDD or GND, e.g 0.1 = 10% of all nets are VDD or GND, both evenly distributed
SUPPLY_PROB = 0.1

#numbers of different element types and current mirror architecturs
TYPES=4
CM_ARCHS=5

# ranges for element parameters
# X_E: exponential value (xE{X_E})
# it is not stated wether the values are positive or negative
MAX_RES_E = 7
MIN_CAP_E = 5
MAX_CAP_E = 15
MOS_MIN = 0.1
MOS_MAX = 10

#######################################



###################### functions   #########################

# debug output
def debug(level,message):
  if(level<=args.DEBUGLEVEL):
    print(message)

# returns new net name
def new_net():
    tmp = random.randrange(100);
    if (tmp < (100*SUPPLY_PROB)/2):
        net = "0"
    elif (tmp < (100*SUPPLY_PROB) ):
        net = "vdd!"
    else: 
        # search for net that is not blocked due use in CM
        # added watchdog
        cnt=0
        while True:
            net = random.randrange(1,int(net_amount))
            cnt += 1
            if (nets[net] != sys.maxsize):
                nets[net] += 1
                break
            if (cnt > int(net_amount)):
                print("Error: CMs are blocking too many nets. (net_amount = " + str(net_amount) + ")" )
                # sys.exit()

        net = "net" + str(net)
    return net

# returns new net name for CM
# assures that net is not reused
def new_CM_net():
    cnt=0
    while True:
        net = random.randrange(1,int(net_amount))
        cnt += 1
        # secure CM nets by setting array value to max_int
        if (nets[net] != sys.maxsize):
            nets[net] = sys.maxsize
            break
        if (cnt > int(net_amount)):
                print("Error: CMs are blocking too many nets. (net_amount = " + str(net_amount) + ")")
                #sys.exit()

    net = "net" + str(net)
    return net


def resistor(element):
    #Rx (N1 N2) R=XXEXX
    
    # assure that both nets never are the same
    while True:
         net1 = new_net()
         net2 = new_net()
         if (net1 != net2):
            break

    resistance = '{0:0.1f}'.format (random.uniform(0.1, 10.0))
    resistance = "R=" + str(resistance) + "E" + str(random.randrange(int(MAX_RES_E)))
              
    result = "R" + str(element) + " (" + str(net1) + " " + str(net2) + ") " + str(resistance) +"\n"
    debug(2,result)
    return result

def capacitor(element):
    #Cx (N1 N2) C=XXE-XX
    # assure that both nets never are the same
    while True:
         net1 = new_net()
         net2 = new_net()
         if (net1 != net2):
            break

    capacitance = '{0:0.1f}'.format (random.uniform(0.1, 10.0))
    capacitance = "C=" + str(capacitance) + "E-" + str(random.randrange(int(MIN_CAP_E), int(MAX_CAP_E)))
              
    result = "C" + str(element) + " (" + str(net1) + " " + str(net2) + ") " + str(capacitance) +"\n"
    debug(2,result)
    return result

def nmos(element):
    #Tx (net1 net2 net3 0) nfet l=XX w=XX
    net1 = new_net()
    net2 = new_net()
    net3 = new_net()
    length = '{0:0.2f}'.format (random.uniform(MOS_MIN, MOS_MAX))
    length = "L=" + length + "E-6"
    width = '{0:0.2f}'.format (random.uniform(MOS_MIN, MOS_MAX))
    width = "W=" + width + "E-6"
              
    result = "T" + str(element) + " (" + str(net1) + " " + str(net2) + " " + str(net2) + " 0) nfet " + length + " " + width +"\n"
    debug(2,result)
    return result

def pmos(element):
    #Tx (net1 net2 net3 0) pfet l=XX w=XX
    net1 = new_net()
    net2 = new_net()
    net3 = new_net()
    length = '{0:0.2f}'.format (random.uniform(MOS_MIN, MOS_MAX))
    length = "L=" + length + "E-6"
    width = '{0:0.2f}'.format (random.uniform(MOS_MIN, MOS_MAX))
    width = "W=" + width + "E-6"
              
    result = "T" + str(element) + " (" + str(net1) + " " + str(net2) + " " + str(net2) + " 0) pfet " + length + " " + width +"\n"
    debug(2,result)
    return result
 
# returns line with elements
def create_element(option,element):
    switcher = {
        0: lambda: resistor(element),
        1: lambda: capacitor(element), 
        2: lambda: nmos(element), 
        3: lambda: pmos(element),
    }
    func = switcher.get(option, lambda: "nothing")
    return func()

# remove floating nets
# TODO
def connect_floating_nets():
    return "\n"


################ CM generation functions ###############
# info: net_in and net_out can be shared with other components, netX not

def CM_arch1(element):
    #simple CM with two FET
    #data:image/png;base64,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
    #Tx (net_i net_in 0 0) xfet l=length w=with
    #Tx (net1  net_in 0 0) xfet l=length w=width
    #Rx (net1  net_out) R=XXEXX

    if (random.random() > 0.5):
        fet = " nfet "
        supply = " 0"
    else:
        fet = " pfet "
        supply = " vdd!"
    
    ele1 = element
    ele2 = ele1 + 1 
    ele3 = ele2 + 1

    net_in  = " " + new_net()
    # assure that both nets of the resistor never are the same
    while True:
        net1    = " " + new_CM_net()
        net_out = " " + new_net()
        if (net1 != net_out):
            break
    

    length = str('{0:0.2f}'.format (random.uniform(MOS_MIN, MOS_MAX)))
    length = " L=" + length + "E-6"
    width = str('{0:0.2f}'.format (random.uniform(MOS_MIN, MOS_MAX)))
    width = " W=" + width + "E-6"
    res = str('{0:0.1f}'.format (random.uniform(0.1, 10.0)))
    res = " R=" + str(res) + "E" + str(random.randrange(int(MAX_RES_E)))    
    
    result = ""
    result = result + "T" + str(ele1) + " (" + net_in + net_in  + supply + supply + ") " + fet + length + width +"\n"
    result = result + "T" + str(ele2) + " (" + net1   + net_in  + supply + supply + ") " + fet + length + width +"\n"
    result = result + "R" + str(ele3) + " (" + net1   + net_out + ") " + res +"\n"
    
    debug(2,result)
    return result

def CM_arch2(element):
    #simple CM with two FET
    #data:image/png;base64,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
    #Rx (net_in  net1) R=XXEXX
    #Tx (net1    net1 0 0) xfet l=length w=width
    #Tx (net_out net1 0 0) xfet l=length w=width
    
    if (random.random() > 0.5):
        fet = " nfet "
        supply = " 0"
    else:
        fet = " pfet "
        supply = " vdd!"
    
    ele1 = element
    ele2 = ele1 + 1 
    ele3 = ele2 + 1
    
   
    net_out = " " + new_net()
    # assure that both nets of the resistor never are the same
    while True:
        net1    = " " + new_CM_net()
        net_in = " " + new_net()
        if (net1 != net_in):
            break

    length = str('{0:0.2f}'.format (random.uniform(MOS_MIN, MOS_MAX)))
    length = " L=" + length + "E-6"
    width = str('{0:0.2f}'.format (random.uniform(MOS_MIN, MOS_MAX)))
    width = " W=" + width + "E-6"
    res = str('{0:0.1f}'.format (random.uniform(0.1, 10.0)))
    res = " R=" + str(res) + "E" + str(random.randrange(int(MAX_RES_E)))    
    
    result = ""
    result = result + "R" + str(ele1) + " (" + net_in  + net1 + ") " + res +"\n"
    result = result + "T" + str(ele2) + " (" + net1    + net1 + supply + supply + ") " + fet + length + width +"\n"
    result = result + "T" + str(ele3) + " (" + net_out + net1 + supply + supply + ") " + fet + length + width +"\n"
    
    debug(2,result)
    return result

def CM_arch3(element):
    #CM with two load FET
    #data:image/png;base64,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
    #Rx (net_in  net1) R=XXEXX
    #Tx (net1    net2 0 0) xfet l=length w=width
    #Tx (net3    net2 0 0) xfet l=length w=width
    #Tx (net_out net1 net3 0) xfet l=length w=width
    
    if (random.random() > 0.5):
        fet = " nfet "
        supply = " 0"
    else:
        fet = " pfet "
        supply = " vdd!"
    
    ele1 = element
    ele2 = ele1 + 1 
    ele3 = ele2 + 1
    ele4 = ele3 + 1
    
    net2    = " " + new_CM_net()
    net3    = " " + new_CM_net()
    net_out = " " + new_net()
    # assure that both nets of the resistor never are the same
    while True:
        net1    = " " + new_CM_net()
        net_in = " " + new_net()
        if (net1 != net_in):
            break
        
    length = str('{0:0.2f}'.format (random.uniform(MOS_MIN, MOS_MAX)))
    length = " L=" + length + "E-6"
    width = str('{0:0.2f}'.format (random.uniform(MOS_MIN, MOS_MAX)))
    width = " W=" + width + "E-6"
    res = str('{0:0.1f}'.format (random.uniform(0.1, 10.0)))
    res = " R=" + str(res) + "E" + str(random.randrange(int(MAX_RES_E)))    
    
    result = ""
    result = result + "R" + str(ele1) + " (" + net_in  + net1 + ") " + res +"\n"
    result = result + "T" + str(ele2) + " (" + net1    + net2 + supply + supply + ") " + fet + length + width +"\n"
    result = result + "T" + str(ele3) + " (" + net3    + net2 + supply + supply + ") " + fet + length + width +"\n"
    result = result + "T" + str(ele4) + " (" + net_out + net1 + net3   + supply + ") " + fet + length + width +"\n"
    
    debug(2,result)
    return result

def CM_arch4(element):
    #CM with extra load FET
    #data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAARMAAAC3CAMAAAAGjUrGAAAAhFBMVEX///8dHR3Ly8vX19cAAADp6enGxsYyMjKQkJD7+/va2tq+vr66urry8vL4+Ph5eXlOTk45OTknJyeHh4enp6djY2MUFBTl5eXz8/NxcXFXV1ff399ra2ufn584ODi1tbVGRkabm5tAQECurq4REREaGhopKSlSUlKBgYFcXFxvb2+cnJyqv4IwAAAImklEQVR4nO2dh2KiMBiAAyRAGAFlLwFxYPv+73cg2qoIonKWke+uTi4HX7MIfwIAFAqFQqFQKBQKhUJ5CsfAb6eBDad8CvK3UxoG3J68nQYJ+fJJPryd0jDg/PedAGdRZDY1Qe+nNAh6cULyGIBsKkXnDScBH/y8dgTg6k4/e/T3FE6wx2uYfD2X83G0gXZ09hmsgeoXitTDNgdI3xr97+gHKZyQRIYpebI24JepYzLK+a0pakXxAZaMzPjAozTuez8/SZlPdHmbB/pzTtJEBe5O/Ekm16TiSecABosA4Pcb+D+kaIuxroSyJjznJBN4wNnmz3sjKh8LJ6B0Mm5UHhA9tkAIn3OCrF24CH+rVe4oYs8CWU4kEMv97mVvqMdH8rBdIXvFAtL6yd6FakCv9k8kfWOp3Nr21OcS+xRIP+6Yed0GuHf2lhR/wNNNsiTcyQyuSk4Pg8TNy1YBGcrFZ1ixfLGnfsRdJ0OH84sHPrz8SNmF4srr57c4SidEjAD64i4+ca2i1ypDz2iD79iOjtIJyDTgJGWmONeF6r7INSxMrEv83ca+AC7ZbqmP0wmvqYpWODH1068em3aa6b5a9KkuIJdgTuC7pT5OJ8DImLKZ0c5OADET4au9SzV1J9zXd2kj+HECsCM96DpM3QmwjjWspD9x+jF5J+goQ0qok1vQM+PQM3HyFNRJHeqkDnVShzqpQ53UoU7qUCd1qJM61EmdzzpBnDOCS0EfdcIlu3U01AHtX/p1gtUW3GBpsSnz/d4Of4BenSBjtVosir/nn+uXzAYBEOpv7vH/p1cn5ibUWgghD5BuvbnH/59+nayltq+JJ3h7veOY+B/ySScAiZYxfCWfdQKwO4Km+MNOxsEHnKjm8LskV3zAiaMPNBSjic5OWOZlJ/vJOtlSJ7fQfFKHOqnznhPir0SMLQzEdZIsOv6Xf8WHnISyI5p4g0GYKUngPrePn+YTToq2WOdAKoJt4YTlBj/H5QNO1IhcOfGf28PPwwkdT8ped1KSSKUTCEbhRBJEpyzexDnSfIr2nhNnsdFUwDN2irnhD6Ckq6XPAZAxekGSNW7XyUnzpB6E3OMjAXjwLbOjhBDGAEQGdl1XXTWGnHdzMv75cCg29KVuZMWRRNU8lObpGjNxgiO40eTqMCKjjBgls3cCWB/afhaUBdyEzHbLMErztjNxUpYebwHXbJVPeK+sIoP7xzUfJyDILAiVU30ifpfzH++3PXNx4pjaendIyyolKuf9cBoHgob2eCZOjnUsXx2GeWx3pIMKDPPuxjNxAliLsfWIK0ONTxPCio5sPm8nhQo+X8PrUx5t7k6AZB6OdewvPHd3w7k4CVJLWIYm3+UMZCZO8DeEGtvxlGwmTgDnLWyDOrmBfNt9jrNNwgmQeh17nIaTXsdjZeF+mzUyenXCd52YO2yokzrUSZ3OTmRInVTIyXEkHksa7LDIyTycxExQGOHyZRJ16NvNxMnSwXy+1KNOHY+5ODE15mTk8epa83CiQLiPKyNpkogPrMzDSQzNKliEh2kQmLD5Wsdxo3k4WVZLhZA0LZ9MsTXUdV5OuMOx2GCr9aCn4wQ3c8dJ2wJwk3FyqE+0yY3zC1+4cgKsWG+paCfjZMPUEJLzK7iqnARW0fiwjmrtHDFtTGwyTloPIzuVHaAICHhaEgPVaD7vmYyT1jrWPDsJxKIk5aKGUN583DNzUmyZZSxgLVUUG7eeh5MMxtftDJe0DPTPxclG46/CnlFLELSym4MTkzH2MDTT705XgWbiZOkQxYIQfnVZcnUmTsoxJWdfSOkyL3geThS/zB/ZWljCDmtxK8zAZ6F044ETfKxRserweYcx6hg2x2GPiM7j9sGqg5NZ5JNfusylnUd98gt1Uoc6qUOd1KFO6lAndaiTOtRJHeqkDnVSh11SJ7d0id1SlpM430HrkD1dxIpbAzmbnXCnLzB/SMZ+b68KWd+Gx/vNEJi3hVI0OsHi8WYuRA7hfsTZBCP0G3cUZMnyi3UB2bTe+rDFiY6Bq1jLfXZK1EVtA9nDxMl03ed+raAs2YWs+roTxPs7XzklSII8SbShr3FyQ1FIEAoE7+IjNdPtEL7qZOfbvvwzsC/DWFXlB9E7Q6O6oyzyrqpUEvsvO4HWxVfVvdaA0nUOzCAg6+qyRHRzjfP1spNcHr60rp73Y+qqkOS+kzfq2MvLp1JSPftjmqJxkU+Cy8b3oZOmhvbGyTmfcJgfzWwebGQA8Jmay8riMtMTO2TPcGyNyE6v3v9u4l05QSEHSMZKnpTujdFIITADsXEIQSRcOdnCM9sVfMhq8/Py+r7zCsOB1GAUEgFrNPc1xryY7A+ZEbtXU9XI1pOVCplXHsKfN1b8q3wCkBImvieHAZDzEbU9LsdJQFXVayf2/QnoD8n1m1BIxHEOcAgQR3hVECXXTqKXUsHarZPT5+laHk198oObXnbA1ZedJHeLiKpp4biXYib8F3zVyUZjx7D09lM4DuEPUH/VSc6s7ZAjzvgKSjOyAHdQ518vOzqS15CBXVdJHD7YLPoltozfqWNxkUrZrRlNd+QBYtnr8tyyK9ccNN4G0cpxNhQWyWxG2PjewRGWmqkcz4CUFwdTueOJUKBEGjOVNf+z3lbkJ9lUYoZ7PAx2Kk56HGufR2z5c1AndWTqpMbcrhd3YTJOejwMeSJOdqHYG9Y06hMiLrf1iaPX2NB+tMmR7Soe2R2ZGiDoEWpsyw83qvjrg/kc/HYSRaJXqJM61EkdBVInt1AndaiTOjF1cgnOPC33oZVr3riCsf4jLEy8itWiy6zrOUAsv7rwGSTNy1nMjXMAY7oYUyzW/wVXGUUSWgO7Zga7K6/uGYtJXLnpCfylI+BsaTa5hFumQKONzhUkT3jmxbCuycLumGmsW98jRIRTCaLoD5WbxjArhUKhUCgUCoVCoQyTfykemZb9D1zEAAAAAElFTkSuQmCC
    #Rx (net_in  net1) R=XXEXX
    #Tx (net1    net2 0    0) nfet l=length w=width
    #Tx (net_out net2 0    0) nfet l=length w=width
    #Tx (vdd!    net1 net2 0) nfet l=length w=width
    
    if (random.random() > 0.5):
        fet = " nfet "
        supply = " 0"
        supply_i = " vdd!"
    else:
        fet = " pfet "
        supply = " vdd!"
        supply_i = " 0"
    
    ele1 = element
    ele2 = ele1 + 1 
    ele3 = ele2 + 1
    ele4 = ele3 + 1
    
    net2    = " " + new_CM_net()
    net_out = " " + new_net()
    # assure that both nets of the resistor never are the same
    while True:
        net1    = " " + new_CM_net()
        net_in = " " + new_net()
        if (net1 != net_in):
            break

    length = str('{0:0.2f}'.format (random.uniform(MOS_MIN, MOS_MAX)))
    length = " L=" + length + "E-6"
    width = str('{0:0.2f}'.format (random.uniform(MOS_MIN, MOS_MAX)))
    width = " W=" + width + "E-6"
    res = str('{0:0.1f}'.format (random.uniform(0.1, 10.0)))
    res = " R=" + str(res) + "E" + str(random.randrange(int(MAX_RES_E)))    
    
    result = ""
    result = result + "R" + str(ele1) + " (" + net_in   + net1 + ") " + res +"\n"
    result = result + "T" + str(ele2) + " (" + net1     + net2 + supply + supply + ") " + fet + length + width +"\n"
    result = result + "T" + str(ele3) + " (" + net_out  + net2 + supply + supply + ") " + fet + length + width +"\n"
    result = result + "T" + str(ele4) + " (" + supply_i + net1 + net2   + supply + ") " + fet + length + width +"\n"
    
    debug(2,result)
    return result

def CM_arch5(element):
    #CM with 4 FET
    #data:image/png;base64,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
    #Rx (net_in  net1) R=XXEXX
    #Tx (net1    net1 net2 0) nfet l=length w=width
    #Tx (net2    net3 0    0) nfet l=length w=width
    #Tx (net3    net3 0    0) nfet l=length w=width
    #Tx (net_out net1 net3 0) nfet l=length w=width
    
    if (random.random() > 0.5):
        fet = " nfet "
        supply = " 0"
        supply_i = " vdd!"
    else:
        fet = " pfet "
        supply = " vdd!"
        supply_i = " 0"
    
    ele1 = element
    ele2 = ele1 + 1 
    ele3 = ele2 + 1
    ele4 = ele3 + 1
    ele5 = ele4 + 1
    
    net2    = " " + new_CM_net()
    net3    = " " + new_CM_net()
    net_out = " " + new_net()
    # assure that both nets of the resistor never are the same
    while True:
        net1    = " " + new_CM_net()
        net_in = " " + new_net()
        if (net1 != net_in):
            break

    length = str('{0:0.2f}'.format (random.uniform(MOS_MIN, MOS_MAX)))
    length = " L=" + length + "E-6"
    width = str('{0:0.2f}'.format (random.uniform(MOS_MIN, MOS_MAX)))
    width = " W=" + width + "E-6"
    res = str('{0:0.1f}'.format (random.uniform(0.1, 10.0)))
    res = " R=" + str(res) + "E" + str(random.randrange(int(MAX_RES_E)))    
    
    result = ""
    result = result + "R" + str(ele1) + " (" + net_in  + net1 + ") " + res +"\n"
    result = result + "T" + str(ele2) + " (" + net1    + net1 + net2   + supply + ") " + fet + length + width +"\n"
    result = result + "T" + str(ele3) + " (" + net2    + net3 + supply + supply + ") " + fet + length + width +"\n"
    result = result + "T" + str(ele4) + " (" + net3    + net3 + supply + supply + ") " + fet + length + width +"\n"
    result = result + "T" + str(ele5) + " (" + net_out + net1 + net3   + supply + ") " + fet + length + width +"\n"
    
    debug(2,result)
    return result

# returns line with elements
def create_CM(option,element):
    switcher = {
        0: lambda: CM_arch1(element),
        1: lambda: CM_arch2(element),
        2: lambda: CM_arch3(element),
        3: lambda: CM_arch4(element),
        4: lambda: CM_arch5(element),
    }
    func = switcher.get(option, lambda: "nothing")
    return func()

# return elements per CM architecture
def CM_elements(option):
    switcher = {
        0: 3,
        1: 3,
        2: 4,
        3: 4,
        4: 5,
    }
    amount = switcher.get(option, "nothing")
    return amount

#######################################

parser = argparse.ArgumentParser(description='Creating of random netlist containing current mirrors')
parser.add_argument('--files', default=1, type=int, help='Number of circuits to be created. (default: 1)')
parser.add_argument('--max_elements', default=1000, type=int, help='Maximum number of elements per circuit. (default: 1000)')
parser.add_argument('--name', default="rcircuit", help='Base name for circuits to be generated. (default: "rcircuit")')
parser.add_argument('--CM', default=0, type=int, help='If CM=1, generate only Current Mirrors (default: 0)')
parser.add_argument('--CM_type', default=0, type=int, help='Choose Current Mirror type (1-5) (if CM_type=0 then random type) (default: 0)')
parser.add_argument('--max_CM', default=1, type=int, help='If CM=1, Max number of Current Mirrors to be integrated (default: 1)')
parser.add_argument('--debug', dest='DEBUGLEVEL', default=0, type=int, help='Level for debug messages. (default: 0)')
args = parser.parse_args()

if (args.CM == 0):
    # generate normal netlist

    #create folder for results and open file
    dir = os.path.join(os.getcwd(), "circuits")
    if not os.path.exists(dir):
        os.makedirs(dir)
    
    # for all files
    for curr_file in range(args.files):
        print ("Create file " + args.name + str(curr_file) + ".sp")
                
        filename=os.path.join(dir, args.name+str(curr_file)+".sp")
        logfilename=os.path.join(dir, args.name+str(curr_file)+".log")
        file=open(filename,"w+")
        logfile=open(logfilename,"w+")

        # random ampunt of elements and nets for circuit
        max_elements=random.randint(10,(10+args.max_elements))
        # assure that enough nets are available
        net_amount=args.max_CM*5 + int(random.randint(1,(1+int(NETS_VS_ELEMENTS  * max_elements))))
        # initialize all nets with 0
        nets=np.zeros(int(net_amount))
            
        CMs = args.max_CM
        element=1
        # create all elements
        while element < max_elements:
            #place CMs
            if (CMs > 0):
                if (random.random() < 0.5): #args.max_CM/max_elements):
                    # random CM or prechosen
                    if (args.CM_type == 0):
                        option  = random.randrange(int(CM_ARCHS))
                    else:
                        option = args.CM_type - 1

                    CM = create_CM(option,element)
                    file.write(CM)                      
                    logfile.write("CM arch: " + str(option+1) + "\n")
                    logfile.write("Netlist: \n" + CM)
                    debug(1,"Create CM (Arch " + str(option+1) + ")")
                    CMs -= 1
                    element += CM_elements(option)
                    
            option = random.randrange(int(TYPES))
            file.write(create_element(option,element))
            element += 1
        
        file.write(connect_floating_nets())        
        file.close()
        logfile.close()
else:
    # Create Current mirrors
    #create folder for results and open file
    dir = os.path.join(os.getcwd(), "CM_circuits")
    if not os.path.exists(dir):
        os.makedirs(dir)

    # for all files
    for curr_file in range(args.files):
        print ("Create file CM" + str(curr_file) + ".sp")
        
        filename    = os.path.join(dir, "cm" + str(curr_file) + ".sp")
        logfilename = os.path.join(dir, "cm" + str(curr_file) + ".log")
        file=open(filename,"w+")
        logfile=open(logfilename,"w+")
        
        # initialize net parameters, assure that enough nets are available
        net_amount = args.max_CM*5 + int(random.randint(1,int(NETS_VS_ELEMENTS  * args.max_elements)))
        nets = np.zeros(net_amount)

        # choose architecture type
        element = random.randint(1,args.max_elements)
        # random CM or prechosen
        if (args.CM_type == 0):
            option  = random.randrange(int(CM_ARCHS))
        else:
            option = args.CM_type - 1
                
        file.write(create_CM(option,element))
        logfile.write("CM arch: " + str(option+1) + "\n")
        file.close()
        logfile.close()
