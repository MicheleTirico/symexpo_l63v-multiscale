import pandas as pd
from toolbox.control import logger
from toolbox.control import handleFiles
from toolbox.control import tools
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

# paths and parametetes
prefix="l63v-multiscale"
scenario=prefix+"_"+"03"
pathOutputDir="outputs/"+scenario+"/"
pathResources="resources/"
pathOutputFig=pathOutputDir+"fig/"

path_mat=pathResources+"od_matrix_01/output_trips.csv"
path_mat_travel_distance=pathOutputDir+prefix+"_mat_travel-distance.csv"
path_sym=pathOutputDir+"l63v-multiscale_000000_235959_traf_trajectoires.csv"
path_sym_travel_distance=pathOutputDir+prefix+"_sym_travel-distance.csv"


# setup fig
sns.set_style("whitegrid")
position_color=[2,3,4]
palette=plt.rcParams['axes.prop_cycle'].by_key()['color']


# logger and handleFiles
# ----------------------------------------------------------------------------------------------------------------------
hf=handleFiles.HandleFiles(logger=None)
hf.createDirectories(["outputs",pathOutputDir,pathOutputFig])
logger=logger.Logger(storeLog=True,initStore=True,pathLog=pathOutputDir+prefix+"_log_traveled-distance.md")
hf.setLogger(logger=logger)
logger.setDisplay(True,True,True,True)
logger.storeLocal(False)
cwd=hf.getDefCwd()
logger.log(cl=None,method=None,message="start traveled-distance")

run_mat,run_sym,run_fig_hist,run_test=False,False,False,True

# ----------------------------------------------------------------------------------------------------------------------
logger.log(cl=None,method=None,message="get number of vehicles per second and per link")

if run_mat:
    logger.log(cl=None,method=None,message="get traveled distance for MATSim")
    df_mat=pd.read_csv(filepath_or_buffer=path_mat,sep=";")

    df_mat=df_mat[df_mat["modes"]=="car"]
    df_mat["dep_time"]=df_mat.apply(lambda row: tools.get_second(row["dep_time"]),axis=1)
    df_mat["trav_time"]=df_mat.apply(lambda row: tools.get_second(row["trav_time"]),axis=1)
    df_mat["end_time"]=df_mat["trav_time"]+df_mat["dep_time"]

    df_mat["ts"]=df_mat["dep_time"]//900
    print (df_mat)
    df_mat=df_mat[tools.dropValColumns(columns=list(df_mat.columns),listValToDrop=[ 'trip_number','wait_time', 'euclidean_distance',
         'main_mode','longest_distance_mode','start_activity_type','end_activity_type', 'start_facility_id', 'start_link', 'start_x',
         'start_y', 'end_facility_id', 'end_link', 'end_x', 'end_y','first_pt_boarding_stop', 'last_pt_egress_stop' ,"person","modes"])]
    print (df_mat)
    tools.storeDataframe(logger=logger,pathStore=path_mat_travel_distance,df=df_mat)

if run_sym:
    logger.log(cl=None,method=None,message="get traveled distance for Symuvia")
    df_sym=pd.read_csv(filepath_or_buffer=path_sym,sep=";")
    df_sym=df_sym[tools.dropValColumns(columns=list(df_sym.columns),listValToDrop=[ 'instC','entree', 'itineraire','sortie', 'lib', 'type', 'vx', 'w'])]
    df_sym=df_sym.rename(columns={"id":"trip_id","instE":"dep_time","instS":"end_time","dstParcourue":"traveled_distance"})
    df_sym=df_sym.dropna()

    df_sym.loc[df_sym["end_time"]==-1,"end_time"]=60*60*24
    df_sym["trav_time"]=df_sym["end_time"]-df_sym["dep_time"]
    df_sym["ts"]=df_sym["dep_time"]//900

    print (df_sym)
    tools.storeDataframe(logger=logger,pathStore=path_sym_travel_distance,df=df_sym)

if run_fig_hist:
    logger.log(cl=None,method=None,message="get figure")
    df_sym=pd.read_csv(filepath_or_buffer=path_sym_travel_distance,sep=";")
    df_mat=pd.read_csv(filepath_or_buffer=path_mat_travel_distance,sep=";")

    quantile=1.0
    log_scale=False
    bins=50
    alpha=0.7

    df1_mat=df_mat[["trip_id","traveled_distance"]]
    df1_mat.insert(loc=2,column="model",value="MATSim")
    df1_sym=df_sym[["trip_id","traveled_distance"]]
    df1_sym.insert(loc=2,column="model",value="Symuvia")
    df1_sym=df1_sym[df1_sym["traveled_distance"]<df1_sym["traveled_distance"].quantile(quantile)]
    df1_mat=df1_mat[df1_mat["traveled_distance"]<df1_mat["traveled_distance"].quantile(quantile)]

    df1=pd.concat([df1_mat,df1_sym]).reset_index()
    df1=df1[df1["traveled_distance"]>=0]

    fig, ax = plt.subplots()
    ax.set(xlabel="traveled distance [m]", ylabel="probability")
    sns.histplot(data=df1, x="traveled_distance",hue="model", multiple="stack",log_scale=log_scale,alpha=alpha,bins=bins,palette=[palette[position_color[0]],palette[position_color[1]]],stat="probability")
    tools.saveFig(fig=fig,pathSave=cwd+pathOutputFig+"{}_{}_{}_quant-{}_log-{}.jpg".format(prefix,"traveled-distance","hist",quantile,log_scale),logger=logger)
    plt.close()

if run_test:
    df_sym=pd.read_csv(filepath_or_buffer=path_sym_travel_distance,sep=";")
    df_mat=pd.read_csv(filepath_or_buffer=path_mat_travel_distance,sep=";")
    print (df_sym)
    print (df_mat)

    df_mat=df_mat.groupby(by="ts").sum().reset_index()
    df_sym=df_sym.groupby(by="ts").sum().reset_index()
    fig, ax = plt.subplots()
    sns.lineplot(data=df_sym, x="ts", y="traveled_distance",label="Symuvia",color=palette[position_color[1]])
    sns.lineplot(data=df_mat, x="ts", y="traveled_distance",label="MATSim",color=palette[position_color[0]])
    ax.set(xlabel='hours [h]', ylabel="traveled distance [m]")
    # plt.xticks([_*60*60 for _ in range(0,25)],list(range(0,25)))
    tools.saveFig(fig=fig,pathSave=cwd+pathOutputFig+"{}_{}_{}_{}.jpg".format(prefix,"traveled-distance","ts","test"),logger=logger)
    plt.close()


