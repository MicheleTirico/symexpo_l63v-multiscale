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

import datetime
symuvia_input="/home/mt_licit/project/symexpo_l63v-multiscale/resources/l63v-multiscale_01/L63V_symuflow_input.xml"
demand_input="/home/mt_licit/project/symexpo_l63v-multiscale/outputs/l63v-multiscale_01/od/l63v-multiscale_od_matrix_sym.csv"

# Load symuvia DLL into memory.
lib_path='/home/mt_licit/anaconda3/envs/symupy/lib/'
lib_name ="libSymuFlow.so" #'libSymuFlow.dylib'

full_name = lib_path+lib_name
os.chdir(lib_path)
os.environ['PATH'] = lib_path + ';' + os.environ['PATH']
symuvia_dll = cdll.LoadLibrary(full_name)

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
        if time%900==0: print("time: "+ str(datetime.timedelta(seconds=time)))

        for index, row in dts.iterrows():
            tc = ct.c_double(row.creation-time)

            if(row.origin!=row.destination):
                # ok = symuvia_dll.SymCreateVehicleWithRouteEx(row.origin.encode('UTF8'), row.destination.encode('UTF8'), row.typeofvehicle.encode('UTF8'), 1, tc,None)
                # ok = symuvia_dll.SymCreateVehicleEx(row.origin.encode('UTF8'), row.destination.encode('UTF8'), row.typeofvehicle.encode('UTF8'), 1, tc)
                ok = symuvia_dll.SymCreateVehicleEx(row.typeofvehicle.encode('UTF-8'), row.origin.encode('UTF-8'),row.destination.encode('UTF-8'),  1, tc)

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




