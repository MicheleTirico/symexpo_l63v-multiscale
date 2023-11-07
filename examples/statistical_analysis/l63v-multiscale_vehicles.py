import pandas as pd
from toolbox.control import logger
from toolbox.control import handleFiles
from toolbox.control import tools
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

# setup fig
sns.set_style("whitegrid")
position_color=[2,3,4]
palette=plt.rcParams['axes.prop_cycle'].by_key()['color']

# paths and parametetes
prefix="l63v-multiscale"
scenario=prefix+"_"+"03"
pathOutputDir="outputs/"+scenario+"/"
pathResources="resources/"
pathOutputFig=pathOutputDir+"fig/"

path_mat=pathResources+"od_matrix_01/output_trips.csv"
path_mat_nveh=pathOutputDir+prefix+"_mat_nVeh.csv"
path_mat_nveh_sum=pathOutputDir+prefix+"_mat_nVeh_sum.csv"

path_sym=pathOutputDir+"l63v-multiscale_000000_235959_traf_trajectoires.csv"
path_sym_nveh=pathOutputDir+prefix+"_sym_nVeh.csv"
path_sym_nveh_sum=pathOutputDir+prefix+"_sym_nVeh_sum.csv"

# logger and handleFiles
# ----------------------------------------------------------------------------------------------------------------------
hf=handleFiles.HandleFiles(logger=None)
hf.createDirectories(["outputs",pathOutputDir,pathOutputFig])
logger=logger.Logger(storeLog=True,initStore=True,pathLog=pathOutputDir+prefix+"_log_vehicles.md")
hf.setLogger(logger=logger)
logger.setDisplay(True,True,True,True)
logger.storeLocal(False)
cwd=hf.getDefCwd()
logger.log(cl=None,method=None,message="start get vehicle per seconds")

run_mat,run_handle_df_mat,run_sym,run_handle_df_sym,run_fig_hist,run_check_vehicles_created=False,False,False,False,False,True

# ----------------------------------------------------------------------------------------------------------------------
logger.log(cl=None,method=None,message="get number of vehicles per second and per link")

if run_mat:
    logger.log(cl=None,method=None,message="get number of vehicles for MATSim")
    df_mat=pd.read_csv(filepath_or_buffer=path_mat,sep=";")

    df_mat=df_mat[tools.dropValColumns(columns=list(df_mat.columns),listValToDrop=[ 'trip_number','wait_time', 'euclidean_distance',
        'main_mode','longest_distance_mode','start_activity_type','end_activity_type', 'start_facility_id', 'start_link', 'start_x',
        'start_y', 'end_facility_id', 'end_link', 'end_x', 'end_y','first_pt_boarding_stop', 'last_pt_egress_stop' ])]

    df_mat=df_mat[df_mat["modes"]=="car"]
    df_mat["dep_time"]=df_mat.apply(lambda row: tools.get_second(row["dep_time"]),axis=1)
    df_mat["trav_time"]=df_mat.apply(lambda row: tools.get_second(row["trav_time"]),axis=1)
    df_mat["end_time"]=df_mat["trav_time"]+df_mat["dep_time"]
    df=pd.DataFrame({"time":list(range(max(df_mat["end_time"])+1)),"nVeh":0})

    i=0
    for index, row in df_mat.iterrows():
        df.loc[row.dep_time:row.trav_time+row.dep_time,"nVeh"]=df["nVeh"]+1
        if i==-10: break
        else:i+=1
    print (df)
    tools.storeDataframe(logger=logger,pathStore=path_mat_nveh,df=df)

if run_handle_df_mat:
    logger.log(cl=None,method=None,message="group by ts")
    df_mat=pd.read_csv(filepath_or_buffer=path_mat_nveh,sep=";")
    df_mat["ts"]=df_mat["time"]//900
    df_mat_sum=df_mat.groupby(by="ts").sum().reset_index()
    print (df_mat)
    tools.storeDataframe(logger=logger,pathStore=path_mat_nveh_sum,df=df_mat)

if run_sym:
    logger.log(cl=None,method=None,message="get number of vehicles for Symuvia")
    df_sym=pd.read_csv(filepath_or_buffer=path_sym,sep=";")
    df_sym=df_sym[tools.dropValColumns(columns=list(df_sym.columns),listValToDrop=[ 'dstParcourue', 'instC','entree', 'itineraire','sortie', 'lib', 'type', 'vx', 'w'])]
    df_sym=df_sym.rename(columns={"instE":"dep_time","instS":"end_time"})
    df_sym=df_sym.dropna()
    df_sym.loc[df_sym["end_time"]==-1,"end_time"]=60*60*24
    df_sym["trav_time"]=df_sym["end_time"]-df_sym["dep_time"]
    print (df_sym)

    df=pd.DataFrame({"time":list(range(int(max(df_sym["end_time"])+1))),"nVeh":0})

    i=0
    for index, row in df_sym.iterrows():
        df.loc[row.dep_time:row.trav_time+row.dep_time,"nVeh"]=df["nVeh"]+1
        if i==-10: break
        else:i+=1
    print (df)
    tools.storeDataframe(logger=logger,pathStore=path_sym_nveh,df=df)

if run_handle_df_sym:
    logger.log(cl=None,method=None,message="group by ts")
    df_sym=pd.read_csv(filepath_or_buffer=path_sym_nveh,sep=";")
    df_sym["ts"]=df_sym["time"]//900
    df_sym_sum=df_sym.groupby(by="ts").sum().reset_index()
    print (df_sym)
    tools.storeDataframe(logger=logger,pathStore=path_sym_nveh_sum,df=df_sym)

if run_fig_hist:
    logger.log(cl=None,method=None,message="get figure")
    df_sym=pd.read_csv(filepath_or_buffer=path_sym_nveh,sep=";")
    df_mat=pd.read_csv(filepath_or_buffer=path_mat_nveh,sep=";")

    quantile=1.0
    log_scale=False
    bins=50
    alpha=0.7
    print (df_sym)

    df1_mat=df_mat[["time","nVeh"]]
    df1_mat.insert(loc=2,column="model",value="MATSim")
    df1_sym=df_sym[["time","nVeh"]]
    df1_sym.insert(loc=2,column="model",value="Symuvia")
    df1_sym=df1_sym[df1_sym["nVeh"]<df1_sym["nVeh"].quantile(quantile)]
    df1_mat=df1_mat[df1_mat["nVeh"]<df1_mat["nVeh"].quantile(quantile)]

    df1=pd.concat([df1_mat,df1_sym]).reset_index()
    df1=df1[df1["nVeh"]>=0]

    fig, ax = plt.subplots()
    ax.set(xlabel="number of vehicles per second [-]", ylabel="probability")
    sns.histplot(data=df1, x="nVeh",hue="model", multiple="stack",log_scale=log_scale,alpha=alpha,bins=bins,palette=[palette[position_color[0]],palette[position_color[1]]],stat="probability")
    tools.saveFig(fig=fig,pathSave=cwd+pathOutputFig+"{}_{}_{}_quant-{}_log-{}.jpg".format(prefix,"nveh","hist",quantile,log_scale),logger=logger)
    plt.close()

if run_check_vehicles_created:
    logger.log(cl=None,method=None,message="check percent of vehicles created at each ts")
    df_sym=pd.read_csv(filepath_or_buffer=path_sym,sep=";")
    df_sym=df_sym[tools.dropValColumns(columns=list(df_sym.columns),listValToDrop=[ 'dstParcourue','entree', 'itineraire', 'lib', 'type', 'vx', 'w'])]
    df_sym["sortie"]=df_sym["sortie"].fillna(0)
    df_sym.loc[df_sym["sortie"]!=0,"sortie"]=1

    df_sym=df_sym.rename(columns={"sortie":"created","instE":"dep_time","instS":"end_time","instC":"created_time"})
    # df_sym=df_sym.dropna()
    df_sym.loc[df_sym["end_time"]==-1,"end_time"]=60*60*24
    df_sym["trav_time"]=df_sym["end_time"]-df_sym["dep_time"]
    df_sym["ts"]=df_sym["created_time"]//900
    df_sym["nVeh"]=1
    print (df_sym)

    df1=df_sym.groupby(by=["ts","created"]).sum().reset_index()
    print (df1)
    df1_tot=df_sym.groupby(by=["ts"]).sum().reset_index()

    fig, ax = plt.subplots()
    sns.lineplot(data=df1, x="ts", y="nVeh",hue="created")
    sns.lineplot(data=df1_tot, x="ts", y="nVeh",label="tot")

    tools.saveFig(fig=fig,pathSave=cwd+pathOutputFig+"{}_{}_{}_{}.jpg".format(prefix,"nVeh","ts","created"),logger=logger)
    plt.close()

