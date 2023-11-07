import pandas as pd
from toolbox.control import logger
from toolbox.control import handleFiles
from toolbox.control import tools

# paths and parametetes
prefix="l63v-multiscale"
scenario=prefix+"_"+"03"
pathOutputDir="outputs/"+scenario+"/"
pathResources="resources/"
pathOutputFig=pathOutputDir+"fig/"

# paths

path_traj_sym=pathOutputDir+"l63v-multiscale_000000_235959_traf_trajectoires.csv"
path_traj_mat=pathResources+"od_matrix_01/output_trips.csv"

path_trip_sym=pathOutputDir+prefix+"_sym_trips.csv"
path_trip_mat=pathOutputDir+prefix+"_mat_trips.csv"
# logger and handleFiles
# ----------------------------------------------------------------------------------------------------------------------
hf=handleFiles.HandleFiles(logger=None)
hf.createDirectories(["outputs",pathOutputDir,pathOutputFig])
logger=logger.Logger(storeLog=True,initStore=True,pathLog=pathOutputDir+prefix+"_log_df-trips.md")
hf.setLogger(logger=logger)
logger.setDisplay(True,True,True,True)
logger.storeLocal(False)
cwd=hf.getDefCwd()
logger.log(cl=None,method=None,message="start create df for MATSim")

run_df_sym,run_df_mat=True,True

# create df
logger.log(cl=None,method=None,message="start create df trips")
# ----------------------------------------------------------------------------------------------------------------------
if run_df_sym:
    df_sym=pd.read_csv(filepath_or_buffer=path_traj_sym,sep=";")
    df_sym['ttt']=df_sym["instS"]-df_sym["instC"]
    df_sym=df_sym.rename(columns={"dstParcourue":"td","instC":"p","id":"trip_id"})
    df_sym["ts"]=df_sym["p"]//900
    df_sym=df_sym[tools.dropValColumns(columns=list(df_sym.columns),listValToDrop=[  'entree',  'instE', 'instS', 'itineraire', 'sortie','lib', 'type', 'vx', 'w', ])]
    df_sym=df_sym.fillna(0)

    print (df_sym)
    tools.storeDataframe(logger=logger,pathStore=path_trip_sym,df=df_sym)                                                    # store df

if run_df_mat:
    df_mat=pd.read_csv(filepath_or_buffer=path_traj_mat,sep=";")
    df_mat=df_mat[tools.dropValColumns(columns=list(df_mat.columns),listValToDrop=[
        'person', 'trip_number','main_mode', 'wait_time', 'euclidean_distance',  'longest_distance_mode', 'start_activity_type',
        'end_activity_type', 'start_facility_id', 'start_link', 'start_x', 'start_y', 'end_facility_id', 'end_link', 'end_x', 'end_y',
        'first_pt_boarding_stop', 'last_pt_egress_stop'
    ])]
    df_mat=df_mat[df_mat["modes"]=="car"]
    df_mat=df_mat.rename(columns={"dep_time":"p","trav_time":"ttt","traveled_distance":"td"})
    df_mat["p"]=df_mat.apply(lambda row: tools.get_second(row["p"]),axis=1)
    df_mat["ttt"]=df_mat.apply(lambda row: tools.get_second(row["ttt"]),axis=1)
    df_mat["ts"]=df_mat["p"]//900
    df_mat=df_mat[tools.dropValColumns(columns=list(df_mat.columns),listValToDrop=[ 'modes'  ])]

    print (df_mat)
    tools.storeDataframe(logger=logger,pathStore=path_trip_mat,df=df_mat)                                                    # store df

