# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 14:54:00 2019

Control zone script

@author: cecile.becarie
"""
from ctypes import cdll, byref
import os
import ctypes as ct
import math
import sys
import math
import csv
import pandas as pd

if len ( sys.argv ) != 4:
    #print(len(sys.argv))
    #sys.exit (" ERROR : the number of arguments is false ")
    folder_input='/Users/cecile.becarie/Dropbox (LICIT_LAB)/ToJiajie/Lyon63V/'
    symuvia_file='L63V_symuflow_input.xml'
    demand_file='L63V_demand.csv'
else:
    folder_input=sys.argv[1]
    symuvia_file=sys.argv[2]
    demand_file=sys.argv[3]

prefix= "l63v-multiscale"#                                "Lafayette"#"5x5grid"
input_xml="L63V_symuflow_input.xml"                                     #        "l63v-multiscale.xml"           #"Lafayette-02"+".xml"#5x5grid.xml"
input_od="l63v-multiscale_od_matrix_sym.csv"

scenario=prefix+"_01"
pathOutputDir="outputs/"+scenario+"/"
pathResources="resources/"+scenario+"/"
path_output_out=pathResources+"OUT/"
path_output_sim=pathOutputDir+"sim/"

# Paths
path_lib="/home/mt_licit/anaconda3/envs/symupy/lib/libSymuFlow.so"#"/home/mt_licit/project/symexpo_l63v-multiscale/env/libSymuFlow.so"
pat_sym_input=pathResources +input_xml
path_sym_od=pathOutputDir +input_od


symuvia_input="/home/mt_licit/project/symexpo_l63v-multiscale/resources/l63v-multiscale_01/L63V_symuflow_input.xml"
demand_input="/home/mt_licit/project/symexpo_l63v-multiscale/outputs/l63v-multiscale_01/l63v-multiscale_od_matrix_sym.csv"


# Load symuvia DLL into memory.
lib_path='/Volumes/Data/GitProjects/symudev/build/lib/'
lib_path='/Users/cecile.becarie/opt/anaconda3/envs/symuflow/lib/'
lib_name = 'libSymuFlow.dylib'

full_name = lib_path+lib_name
os.chdir("/home/mt_licit/anaconda3/envs/symupy/lib/")
os.environ['PATH'] = lib_path + ';' + os.environ['PATH']
symuvia_dll = cdll.LoadLibrary(path_lib)

if symuvia_dll is None:
    print('error: Symuvia not loaded !')

# SymuVia input loading
m = symuvia_dll.SymLoadNetworkEx(symuvia_input.encode('UTF8'))
if(m!=1):
    print('error: SymuVia input file not loaded !')
else:
    print('SymuVia input data are loaded')

print('Network loading: OK')

# demand loading
demand = pd.read_csv(demand_input,sep=";")   #columns: origin;typeofvehicle;creation;path;destination
print('Demand loading: OK')

# Init
time=0
tmptime=0

bEnd = ct.c_int(0)
VNC=0
VC=0
#------------------------
# Time step flow calculation
#------------------------
while(bEnd.value==0):

    # Vehicles creation (warning: vehicules with time creation between 0 and 1 are not generated)
    if(time>0):
        squery = str(time) + ' < creation <= ' + str(time+1)
        dts = demand.query(squery)

        for index, row in dts.iterrows():
            tc = ct.c_double(row.creation-time)

            if(row.origin!=row.destination):
                ok = symuvia_dll.SymCreateVehicleEx(row.origin.encode('UTF8'), row.destination.encode('UTF8'), row.typeofvehicle.encode('UTF8'), 1, tc)
                # ok = symuvia_dll.SymCreateVehicleWithRouteEx(row.origin.encode('UTF8'), row.destination.encode('UTF8'), row.typeofvehicle.encode('UTF8'), 1, tc, row.path.encode('UTF8'))
                if(ok<0):
                    print('Vehicle not created: ', ok, ' ', row)
                    VNC=VNC+1
                else:
                    VC=VC+1

            else:
                print('Vehicle not created: ', row)
                VNC=VNC+1


    # Time step calculation
    ok = symuvia_dll.SymRunNextStepLiteEx(1, byref(bEnd))
    time=time+1
    tmptime = tmptime+1
    if(bEnd.value!=0):
        symuvia_dll.SymUnloadCurrentNetworkEx()
        print(f'Microscopic simulation completed')
        print(VC, ' ', VNC)

del symuvia_dll




