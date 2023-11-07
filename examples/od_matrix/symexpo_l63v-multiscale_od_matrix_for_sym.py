import pandas as pd
import numpy as np
from toolbox.control import logger
from toolbox.control import handleFiles
from toolbox.control import tools
import math as mt
import os
import datetime
import time

# paths and parametetes
prefix="l63v-multiscale"
scenario=prefix+"_"+"03"
pathOutputDir="outputs/"+scenario+"/"
pathOutputDir_od=pathOutputDir+"od/"
pathResources="resources/"
pathResources_od=pathResources+"od_matrix_01/"

path_od=pathOutputDir_od+prefix+"_od_matrix.csv"
path_od_se=pathOutputDir_od+prefix+"_od_matrix_se.csv"

path_od_sym=pathOutputDir_od+prefix+"_od_matrix_sym.csv"

pathPoints=pathResources_od+"symexpo_l63v_sym_points.csv"
path_od_newRep=pathOutputDir_od+prefix+"_od_matrix_sym_newRep_out.csv"

# logger and handleFiles
# ----------------------------------------------------------------------------------------------------------------------
hf=handleFiles.HandleFiles(logger=None)
hf.createDirectories([pathOutputDir])
logger=logger.Logger(storeLog=True,initStore=True,pathLog=pathOutputDir_od+prefix+"_log_od_matrix.md")
hf.setLogger(logger=logger)
logger.setDisplay(True,True,True,True)
logger.storeLocal(False)
cwd=hf.getDefCwd()
logger.log(cl=None,method=None,message="start to create df for ports symuvia")

# read df
# ----------------------------------------------------------------------------------------------------------------------
df_od=pd.read_csv(path_od,sep=";")
# df_od=pd.read_csv(path_od_se,sep=";")

df_od=df_od[tools.dropValColumns(columns=list(df_od.columns),listValToDrop=['Unnamed: 0.1', 'Unnamed: 0', 'trip_id',   'start_x',
                                                                            'start_y', 'end_x', 'end_y', 'is_end', 'is_start', 'is_outside',
                                                                            'is_inside', 'id_port_exit', 'min_dist_exit', 'id_port_entry',
                                                                            'min_dist_entry'])]

df_od_sym=df_od.rename(columns={"node_start":"origin",
                                "modes":"typeofvehicle",
                                "dep_time":"creation",
                                "node_end":"destination"
                                })
df_od_sym["typeofvehicle"]="VL"

df_od_sym["creation"]=df_od_sym.apply(lambda row: tools.get_second(row["creation"]),axis=1)
day=24*60*60
df_od_sym["creation"]=df_od_sym["creation"]-df_od_sym["creation"]//day*day

df_od_sym=df_od_sym.sort_values(by=['creation']).reset_index()
df_od_sym=df_od_sym.rename(columns={"index":"id"})
print (df_od_sym)

# select ok enter and exit
df_od_sym.insert(0, 'id_2', range(1, 1 + len(df_od_sym)))
l_id=           list(df_od_sym.loc[df_od_sym['id_2'].mod(2).eq(0)]["id"])
l_creation=     list(df_od_sym.loc[df_od_sym['id_2'].mod(2).eq(0)]["creation"])
l_typeofvehicle=list(df_od_sym.loc[df_od_sym['id_2'].mod(2).eq(0)]["typeofvehicle"])
l_origin=       list(df_od_sym.loc[df_od_sym['id_2'].mod(2).eq(1)]["origin"])
l_destination=  list(df_od_sym.loc[df_od_sym['id_2'].mod(2).eq(0)]["destination"])

df_final=pd.DataFrame({"id":l_id,
                        "creation":l_creation,
                       "typeofvehicle":l_typeofvehicle,
                       "origin":l_origin,
                       "destination":l_destination
                       })


print (df_final)

tools.storeDataframe(logger=logger,pathStore=path_od_sym,df=df_final)



# def test_destination(val):
#     # print (val)
#     # print (type(val))
#     if val.find("R_")==False: return df_points[df_points["ID"]==val]["OutLinkID_"]
#     else: return 0
#
#
# if runChangeRepartiteurs:
#     logger.log(cl=None,method=None,message="change rep ")
#     df_points=pd.read_csv(pathPoints,sep=";")
#     print (df_points)
#     a = df_points[df_points["ID"].str.contains("R_")]#["OutLinkID_"]
#
#     df_final["new_origin"]=df_final.apply(lambda row:test_destination(row["origin"]),axis=1)
#     quit()
#
#     # df_distance_filtred["node_start"]=df_distance_filtred.apply(lambda row: _test_inside(row["is_inside"],row["start_x"],row["start_y"],row["id_port_entry"],False),axis=1)
#
#     quit()
#     # print (df_points[["ID","OutLinkID_"]])
#     df_points=df_points[["ID","OutLinkID_"]]
#
#     print (df_od_sym)
#     df_merged=pd.merge(df_od_sym,df_points[["ID","OutLinkID_"]], left_on="destination",right_on='ID', how="left")
#     print (df_merged)
#     df_merged.loc[df_merged["destination"].str.contains("R_"),"destination"]=df_merged["OutLinkID_"]
#     # df_od_sym.loc[df_od_sym["destination"].str.contains("R_"),"destination"]=df_points.query("ID=='destination'")["points"] df_points.loc[df_points['ID'] == df_od_sym['destination'], "IncLinkID_"]
#     # df_points[df_points["ID"]==df_points["IncLinkID_"]]
#     # df_merged=df_merged[["id","creation","typeofvehicle","origin","destination"]]
#     print (df_merged)
#     tools.storeDataframe(logger=logger,pathStore=path_od_newRep,df=df_merged)
#
