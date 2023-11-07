from ctypes import cdll, byref
import ctypes as ct
import pandas as pd
import datetime

#---------------------------------------------------------------------------
# paths and parametetes
path_lib=""
path_sym_od="l63v-multiscale_od_matrix_sym.csv"
pat_sym_input="L63V_symuflow_input.xml"

# ----------------------------------------------------------------------------------------------------------------------
print ("start run simulation with demand")
# Load symuflow libray into memory.
print ("start load lib")
symuflow_lib = cdll.LoadLibrary(path_lib)
if symuflow_lib is None:
    print ("Symuflow lib not load, error not defined")
    quit()

# SymuVia input loading
m = symuflow_lib.SymLoadNetworkEx(pat_sym_input.encode('UTF8'))
if(m!=1):
    print ("SymuVia input file not loaded !, error not defined")
    quit()
else:   print ("SymuVia input data are loaded")

# demand loading
print ("Load demand")
demand = pd.read_csv(path_sym_od,sep=";")
print (demand)

# simulation
time,tmptime,bEnd ,period,VNC,VC=0,0,ct.c_int(0),0,0,0
print ("start simulation")

while(bEnd.value==0):
    # Vehicles creation (warning: vehicules with time creation between 0 and 1 are not generated)
    if(time>0):
        squery = str(time) + ' < creation <= ' + str(time+1)
        dts = demand.query(squery)
        if time%60==0: print ("time: "+ str(datetime.timedelta(seconds=time)))
        for index, row in dts.iterrows():
            tc = ct.c_double(row.creation-time)
            if(row.origin!=row.destination):
                # print ("1 {}".format(time))

                ok = symuflow_lib.SymCreateVehicleEx(row.typeofvehicle.encode('UTF-8'), row.origin.encode('UTF-8'),row.destination.encode('UTF-8'),  1, tc)
                if(ok<0):
                    print ('Vehicle not created. Id {}, creation: {}, origin: {}, destination: {}, type of vehicle: {}'.format(row.id,row.creation,row.origin.encode('UTF8'), row.destination.encode('UTF8'), row.typeofvehicle.encode('UTF8')),doQuit=False)
                    VNC=VNC+1
                else:
                    # print ('Vehicle created. Id {}, creation: {}, origin: {}, destination: {}, type of vehicle: {}'.format(row.id,row.creation,row.origin.encode('UTF8'), row.destination.encode('UTF8'), row.typeofvehicle.encode('UTF8')))
                    VC=VC+1
            else:
                print ('Vehicle not created. origin and destination are the same. Id {}, creation: {}, origin: {}, destination: {}, type of vehicle: {}'.format(row.id,row.creation,row.origin.encode('UTF8'), row.destination.encode('UTF8'), row.typeofvehicle.encode('UTF8')),doQuit=False)
                VNC=VNC+1

    # Time step calculation
    ok = symuflow_lib.SymRunNextStepLiteEx(1, byref(bEnd))
    time=time+1
    tmptime = tmptime+1

    if(bEnd.value!=0):
        symuflow_lib.SymUnloadCurrentNetworkEx()
        print(f'Microscopic simulation completed')
        print(VC, ' ', VNC)

del symuflow_lib

