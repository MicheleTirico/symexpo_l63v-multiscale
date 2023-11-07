import pandas as pd
import numpy as np
from toolbox.control import logger
from toolbox.control import handleFiles
from toolbox.control import tools
import math as mt
import os

# paths and parametetes
prefix="l63v-multiscale"
scenario=prefix+"_"+"03"
pathOutputDir="outputs/"+scenario+"/"
pathOutputDir_od=pathOutputDir+"od/"
pathResources="resources/"
pathResources_od=pathResources+"od_matrix_01/"

path_points_distance=pathOutputDir_od+prefix+"_mat_point_distances_all.csv"
path_points_distance_filtred=pathOutputDir_od+"symexpo_l63v_mat_point_all_merged_filtered.csv"
path_dist_inside=pathOutputDir_od+prefix+"_dist_points.csv"
path_points_mat=pathOutputDir_od+"l63v-multiscale_mat_point_distances_all.csv"
path_points_sym=pathResources_od+"symexpo_l63v_sym_points.csv"
path_od_se=pathOutputDir_od+prefix+"_od_matrix_se.csv"
path_od=pathOutputDir_od+prefix+"_od_matrix.csv"


onlySandE=False

# logger and handleFiles
# ----------------------------------------------------------------------------------------------------------------------
hf=handleFiles.HandleFiles(logger=None)
hf.createDirectories([pathOutputDir,pathOutputDir_od])
logger=logger.Logger(storeLog=True,initStore=True,pathLog=pathOutputDir_od+prefix+"_log_od_matrix.md")
hf.setLogger(logger=logger)
logger.setDisplay(True,True,True,True)
logger.storeLocal(False)
cwd=hf.getDefCwd()
logger.log(cl=None,method=None,message="start to create df for ports symuvia")

# ----------------------------------------------------------------------------------------------------------------------

# filter df distance
logger.log(cl=None,method=None,message="create df distance filtered if it does not exist")
df_mat_points=pd.read_csv(path_points_distance,sep=";")
df_distance_filtred=df_mat_points[tools.dropValColumns(columns=list(df_mat_points.columns),listValToDrop=['Unnamed: 0.1', 'Unnamed: 0', 'start_link',  'end_link',"X","Y"])]
df_distance_filtred=df_distance_filtred.rename(columns={"X":"x_mat","Y":"y_mat"})
tools.storeDataframe(logger=logger,pathStore=path_points_distance_filtred,df=df_distance_filtred)

# read csv
logger.log(cl=None,method=None,message="read csv")
df_distance_filtred=pd.read_csv(path_points_distance_filtred,sep=";")
print (df_distance_filtred)
# quit()
# test with a subpart of the df
doTest=False
if doTest:
    logger.log(cl=None,method=None,message="test with a subpart of the df")
    limit=1000
    df_distance_filtred=df_distance_filtred.iloc[:limit]

# get start and end point inside
logger.log(cl=None,method=None,message="start add points outside")
def _test_outside(outside,startOrEnd,port_entryOrExit):
    if outside==1.0 and startOrEnd==1.0:        return port_entryOrExit

df_distance_filtred["node_start"]=df_distance_filtred.apply(lambda row: _test_outside(row["is_outside"],row["is_start"],row["id_port_entry"]),axis=1)
df_distance_filtred["node_end"]=df_distance_filtred.apply(lambda row: _test_outside(row["is_outside"],row["is_end"],row["id_port_exit"]),axis=1)
logger.log(cl=None,method=None,message="end add points outside")

# get inside
logger.log(cl=None,method=None,message="start add points inside")
df_points_mat=pd.read_csv(path_points_mat,sep=";")
df_points_sym=pd.read_csv(path_points_sym,sep=";")
df_points_mat=df_points_mat[tools.dropValColumns(columns=list(df_points_mat.columns),listValToDrop=['Unnamed: 0.1', 'Unnamed: 0', ])]
df_points_inside=df_points_mat[df_points_mat["is_inside"]==1.0]
if onlySandE:
    df_points_sym=df_points_sym[df_points_sym["ID"].str.contains("E_") | df_points_sym["ID"].str.contains("S_")]
list_x,list_y,list_id=list(df_points_sym["X"]),list(df_points_sym["Y"]),list(df_points_sym["ID"])
def _ret_id_dist(x,y,is_entry):
    min_dist=100000000000
    id=None
    for i in range(len(list_id)):
        dist= mt.pow(mt.pow(x-list_x[i],2) + mt.pow(y-list_y[i],2),0.5)
        if is_entry:
            if list_id[i].split("_")[0]!="E":
                if dist < min_dist:
                    min_dist=dist
                    id=list_id[i]
        else:
            if list_id[i].split("_")[0]!="S":
                if dist < min_dist:
                    min_dist=dist
                    id=list_id[i]

    return id
def _test_inside(inside,x,y,previous_val,is_entry):
    if inside==1.0:
        return _ret_id_dist(x,y,is_entry)
    else:
        return previous_val

logger.log(cl=None,method=None,message="start apply entry")
df_distance_filtred["node_start"]=df_distance_filtred.apply(lambda row: _test_inside(row["is_inside"],row["start_x"],row["start_y"],row["id_port_entry"],False),axis=1)
logger.log(cl=None,method=None,message="start apply exit")
df_distance_filtred["node_end"]=df_distance_filtred.apply(lambda row: _test_inside(row["is_inside"],row["end_x"],row["end_y"],row["id_port_exit"],True),axis=1)

print (df_distance_filtred)
logger.log(cl=None,method=None,message="end add points inside")

if onlySandE:   pathStore=path_od_se
else:           pathStore=path_od

tools.storeDataframe(logger=logger,pathStore=pathStore,df=df_distance_filtred)




























#
# if os.path.exists(path_trips_mat_filtred)==False:
#     logger.log(cl=None,method=None,message="create df trips if it does not exist")
#     df_trips_mat=pd.read_csv(path_trips_mat,sep=";")
#     print (df_trips_mat.columns)
#     df_trips_mat_filtred=df_trips_mat[tools.dropValColumns(columns=list(df_trips_mat.columns),listValToDrop=[
#         'person', 'trip_number', 'trav_time', 'wait_time', 'traveled_distance', 'euclidean_distance', 'main_mode',
#         'longest_distance_mode', 'start_activity_type', 'end_activity_type', 'start_facility_id', 'start_link',
#         'end_facility_id', 'end_link',  'first_pt_boarding_stop', 'last_pt_egress_stop'
#     ])]
#     df_trips_mat_filtred=df_trips_mat_filtred[df_trips_mat_filtred["modes"]=="car"]
#     tools.storeDataframe(logger=logger,pathStore=path_trips_mat_filtred,df=df_trips_mat_filtred)





# df_distance_filtred.loc[df_distance_filtred["is_outside"]==1.0 and df_distance_filtred["is_start"]==1.0,"start_sym" ]="peppe"

# df_points_merged.loc[df_points_merged["layer"].str.contains("end"), 'is_end'] = 1
# df_distance_filtred["start_sym"]=df_distance_filtred[df_distance_filtred["is_outside"]==1.0 and df_distance_filtred["is_start"]==1.0]




# def test_outside_start(outside,start,port_entry):
#     if outside==1.0 and start==1.0:        return port_entry
#
# def test_outside_exit(outside,end,port_exit):
#     if outside==1.0 and end==1.0:        return port_exit

# df_trips_mat_filtred=pd.read_csv(path_trips_mat_filtred,sep=";")
# print (df_trips_mat_filtred)
#
# df1=df_distance_filtred[df_distance_filtred["trip_id"]=="1000294_1"]
# print (df1)
# df1=df_trips_mat_filtred[df_trips_mat_filtred["trip_id"]=="1000294_1"]
# print (df1)
#
# df_dist_inside=pd.read_csv(path_dist_inside,sep=";")
# print (df_dist_inside)
#
# df2=pd.merge(df_distance_filtred,df_dist_inside)