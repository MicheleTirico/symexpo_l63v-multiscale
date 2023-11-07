import pandas as pd
import numpy as np
from toolbox.control import logger
from toolbox.control import handleFiles
from toolbox.control import tools
import math as mt

# paths and parametetes
prefix="l63v-multiscale"
scenario=prefix+"_"+"03"
pathOutputDir="outputs/"+scenario+"/"
pathOutputDir_od=pathOutputDir+"od/"
pathResources="resources/"
pathResources_od=pathResources+"od_matrix_01/"

path_ports_entry=pathResources_od+"symexpo_l63v_sym_port_entry.csv"
path_ports_exit=pathResources_od+"symexpo_l63v_sym_port_exit.csv"
path_points_merged_filtered=pathOutputDir_od+"symexpo_l63v_mat_point_all_merged_filtered.csv"
path_points_distance=pathOutputDir_od+prefix+"_mat_point_distances_all.csv"

# logger and handleFiles
# ----------------------------------------------------------------------------------------------------------------------
hf=handleFiles.HandleFiles(logger=None)
hf.createDirectories([pathOutputDir,pathOutputDir_od])
logger=logger.Logger(storeLog=True,initStore=True,pathLog=pathOutputDir_od+prefix+"_log_od_get_distance.md")
hf.setLogger(logger=logger)
logger.setDisplay(True,True,True,True)
logger.storeLocal(False)
cwd=hf.getDefCwd()
logger.log(cl=None,method=None,message="start to create df distances")

# read df
# ----------------------------------------------------------------------------------------------------------------------
df_mat_points=pd.read_csv(path_points_merged_filtered,sep=";")
print (df_mat_points)

df_ports_entry=pd.read_csv(path_ports_entry,sep=";")
df_ports_exit=pd.read_csv(path_ports_exit,sep=";")

df_ports=pd.concat([df_ports_entry,df_ports_exit])
list_x_exit,list_y_exit,list_id_exit=list(df_ports_exit["X"]),list(df_ports_exit["Y"]),list(df_ports_exit["ID"])
list_x_entry,list_y_entry,list_id_entry=list(df_ports_entry["X"]),list(df_ports_entry["Y"]),list(df_ports_entry["ID"])

def _ret_id_dist_exit(x,y):
    min_dist=100000000000
    id=None
    for i in range(len(list_id_exit)):
        dist= mt.pow(mt.pow(x-list_x_exit[i],2) + mt.pow(y-list_y_exit[i],2),0.5)
        if dist < min_dist:
            min_dist=dist
            id=list_id_exit[i]
    return [id ,min_dist]

def _ret_id_dist_entry(x,y):
    min_dist=100000000000
    id=None
    for i in range(len(list_id_entry)):
        dist= mt.pow(mt.pow(x-list_x_entry[i],2) + mt.pow(y-list_y_entry[i],2),0.5)
        if dist < min_dist:
            min_dist=dist
            id=list_id_entry[i]
    return [id ,min_dist]
print (df_ports)

df_mat_points["id_port_exit"]=df_mat_points.apply(lambda row: _ret_id_dist_exit(row['X'], row['Y'])[0], axis=1)
df_mat_points["min_dist_exit"]=df_mat_points.apply(lambda row: _ret_id_dist_exit(row['X'], row['Y'])[1], axis=1)

df_mat_points["id_port_entry"]=df_mat_points.apply(lambda row: _ret_id_dist_entry(row['X'], row['Y'])[0], axis=1)
df_mat_points["min_dist_entry"]=df_mat_points.apply(lambda row: _ret_id_dist_entry(row['X'], row['Y'])[1], axis=1)



print (df_mat_points)
tools.storeDataframe(logger=logger,pathStore=path_points_distance,df=df_mat_points)
