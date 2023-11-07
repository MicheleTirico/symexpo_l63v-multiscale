import pandas as pd
import numpy as np
from toolbox.control import logger
from toolbox.control import handleFiles
from toolbox.control import tools
import math as mt

# paths and parametetes
prefix="l63v-multiscale"
scenario=prefix+"_"+"01"
pathOutputDir="outputs/"+scenario+"/"
pathOutputDir_od=pathOutputDir+"od/"
pathResources="resources/"
pathResources_od=pathResources+"od_matrix_01/"

path_ports_entry=pathResources_od+"symexpo_l63v_sym_port_entry.csv"
path_ports_exit=pathResources_od+"symexpo_l63v_sym_port_exit.csv"
path_points_merged_filtered=pathResources_od+"symexpo_l63v_mat_point_all_merged_filtered.csv"
path_points_distance=pathOutputDir_od+prefix+"_mat_point_distances_all.csv"

# logger and handleFiles
# ----------------------------------------------------------------------------------------------------------------------
hf=handleFiles.HandleFiles(logger=None)
hf.createDirectories([pathOutputDir,pathOutputDir_od])
logger=logger.Logger(storeLog=True,initStore=True,pathLog="outputs/"+scenario+"/"+prefix+"_log_od_get_closest.md")
hf.setLogger(logger=logger)
logger.setDisplay(True,True,True,True)
logger.storeLocal(False)
cwd=hf.getDefCwd()
logger.log(cl=None,method=None,message="start to create df closest")

# read df
# ----------------------------------------------------------------------------------------------------------------------
df_mat_points=pd.read_csv(path_points_merged_filtered,sep=";")
print (df_mat_points)

df_ports_entry=pd.read_csv(path_ports_entry,sep=";")
df_ports_exit=pd.read_csv(path_ports_exit,sep=";")

df_ports=pd.concat([df_ports_entry,df_ports_exit])
list_x,list_y,list_id=list(df_ports["X"]),list(df_ports["Y"]),list(df_ports["Indice"])

def _ret_id_dist(x,y):
    min_dist=100000000000
    id=None
    for i in range(len(list_id)):
        dist= mt.pow(mt.pow(x-list_x[i],2) + mt.pow(y-list_y[i],2),0.5)
        if dist < min_dist:
            min_dist=dist
            id=list_id[i]
    return [id ,min_dist]

print (df_ports)
df_mat_points["id_port"]=df_mat_points.apply(lambda row: _ret_id_dist(row['X'], row['Y'])[0], axis=1)
df_mat_points["min_dist"]=df_mat_points.apply(lambda row: _ret_id_dist(row['X'], row['Y'])[1], axis=1)
df_mat_points=pd.merge(df_mat_points,df_ports[["Indice","ID","Type"]],left_on="id_port",right_on="Indice")
print (df_mat_points)
tools.storeDataframe(logger=logger,pathStore=path_points_distance,df=df_mat_points)
