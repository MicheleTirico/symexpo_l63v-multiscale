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

path_ports=pathResources_od+"symexpo_l63v_sym_port.csv"
path_points_sym=pathResources_od+"symexpo_l63v_sym_points.csv"
path_points_mat=pathOutputDir_od+"l63v-multiscale_mat_point_distances_all.csv"
path_dist_inside=pathOutputDir_od+prefix+"_dist_points.csv"
# logger and handleFiles
# ----------------------------------------------------------------------------------------------------------------------
hf=handleFiles.HandleFiles(logger=None)
hf.createDirectories([pathOutputDir,pathOutputDir_od])
logger=logger.Logger(storeLog=True,initStore=True,pathLog=pathOutputDir_od+prefix+"_log_od_get_distances-points.md")
hf.setLogger(logger=logger)
logger.setDisplay(True,True,True,True)
logger.storeLocal(False)
cwd=hf.getDefCwd()
logger.log(cl=None,method=None,message="start to create df for distances points inside")

# read df
# ----------------------------------------------------------------------------------------------------------------------
# read
df_points_sym=pd.read_csv(path_points_sym,sep=";")
df_points_mat=pd.read_csv(path_points_mat,sep=";")
df_ports=pd.read_csv(path_ports,sep=";")

df_points_sym=df_points_sym[tools.dropValColumns(columns=list(df_points_sym.columns),listValToDrop=['IncLinkID_', 'IncLinkI_1', 'IncLinkI_2','IncLinkI_3', 'IncLinkI_4', 'IncLinkI_5', 'OutLinkID_', 'OutLinkI_1',    'OutLinkI_2', 'OutLinkI_3', 'OutLinkI_4', 'OutLinkI_5'])]
df_points_mat=df_points_mat[tools.dropValColumns(columns=list(df_points_mat.columns),listValToDrop=['Unnamed: 0.1', 'Unnamed: 0', ])]

print (df_ports)
print (df_points_sym)
print (df_points_mat)
print (df_ports.columns)
print (df_points_sym.columns)
print (df_points_mat.columns)

df_points_inside=df_points_mat[df_points_mat["is_inside"]==1.0]

print (df_points_inside)

list_x,list_y,list_id=list(df_points_sym["X"]),list(df_points_sym["Y"]),list(df_points_sym["ID"])
def _ret_id_dist(x,y):
    min_dist=100000000000
    id=None
    for i in range(len(list_id)):
        dist= mt.pow(mt.pow(x-list_x[i],2) + mt.pow(y-list_y[i],2),0.5)
        if dist < min_dist:
            min_dist=dist
            id=list_id[i]
    return [id ,min_dist]

df_points_inside["id_close"]=df_points_inside.apply(lambda row: _ret_id_dist(row['X'], row['Y'])[0], axis=1)
print (df_points_inside)
tools.storeDataframe(logger=logger,pathStore=path_dist_inside,df=df_points_inside)
