from ctypes import cdll, byref
import ctypes as ct
import pandas as pd
import datetime
from toolbox.control import logger
from toolbox.control import handleFiles

#---------------------------------------------------------------------------
# paths and parametetes
prefix= "l63v-multiscale"#                                "Lafayette"#"5x5grid"
input_xml="l63v-multiscale.xml"           #"Lafayette-02"+".xml"#5x5grid.xml"
input_od="l63v-copert_od_matrix_sym.csv"

scenario=prefix
pathOutputDir="outputs/"+scenario+"/"
pathResources="resources/"+scenario+"/"
path_output_out=pathResources+"OUT/"
path_output_sim=pathOutputDir+"sim/"

# Paths
path_lib="/lib/libSymuFlow.so"
pat_sym_input=pathResources +input_xml
path_sym_od=pathResources +input_od

# logger and handleFiles
# ----------------------------------------------------------------------------------------------------------------------
hf=handleFiles.HandleFiles(logger=None)
hf.createDirectories(["outputs",pathOutputDir,path_output_sim])
logger=logger.Logger(storeLog=True,initStore=True,pathLog=pathOutputDir+prefix+"_log_run_simulation_with_od.md")
hf.setLogger(logger=logger)
logger.setDisplay(True,True,True,True)
logger.storeLocal(False)
cwd=hf.getDefCwd()
logger.log(cl=None,method=None,message="start run simulation with demand")

#---------------------------------------------------------------------------

# Load symuflow libray into memory.
logger.log(cl=None,method=None,message="start load lib")
symuflow_lib = cdll.LoadLibrary(path_lib)

if symuflow_lib is None:   logger.error(cl=None,method=None,message="Symuflow lib not load",error="not defined")

# SymuVia input loading
m = symuflow_lib.SymLoadNetworkEx(pat_sym_input.encode('UTF8'))
if(m!=1):   logger.error(cl=None,method=None,message="SymuVia input file not loaded !",error="not defined")
else:   logger.log(cl=None,method=None,message="SymuVia input data are loaded")

# demand loading
logger.log(cl=None,method=None,message="Load demand")
demand = pd.read_csv(path_sym_od,sep=";")   #columns: origin;typeofvehicle;creation;path;destination

# Init
time,bEnd ,period,VNC,VC=0,ct.c_int(0),0,0,0

#------------------------
# Time step flow calculation
logger.log(cl=None,method=None,message="start simulation")

#------------------------
while(bEnd.value==0):

    # Vehicles creation (warning: vehicules with time creation between 0 and 1 are not generated)
    if(time>0):
        if time%900==0: logger.log(cl=None,method=None,message="time: "+ str(datetime.timedelta(seconds=time)))
        squery = str(time) + ' < creation <= ' + str(time+1)
        dts = demand.query(squery)
        for index, row in dts.iterrows():
            tc = ct.c_double(row.creation-time)
            # print(row)
            if(row.origin!=row.destination):
                ok = symuflow_lib.SymCreateVehicleEx(row.origin.encode('UTF8'), row.destination.encode('UTF8'), row.typeofvehicle.encode('UTF8'), 1, tc)
                if(ok<0):
                    logger.warning(cl=None,method=None,message='Vehicle not created. Creation: {}, origin: {}, destination: {}, type of vehicle: {}'.format(time,row.origin.encode('UTF8'), row.destination.encode('UTF8'), row.typeofvehicle.encode('UTF8')),doQuit=False)
                    VNC=VNC+1
                else:  VC=VC+1
            else:
                logger.warning(cl=None,method=None,message='Vehicle not created. Creation: {}, origin: {}, destination: {}, type of vehicle: {}'.format(time,row.origin.encode('UTF8'), row.destination.encode('UTF8'), row.typeofvehicle.encode('UTF8')),doQuit=False)
                VNC=VNC+1

    # Time step calculation
    ok = symuflow_lib.SymRunNextStepLiteEx(1, byref(bEnd))
    time=time+1

    if(bEnd.value!=0):
        symuflow_lib.SymUnloadCurrentNetworkEx()
        print(f'Microscopic simulation completed')
        print(VC, ' ', VNC)

del symuflow_lib

hf.copyFilesFromDirectory(path_output_out,path_output_sim)
