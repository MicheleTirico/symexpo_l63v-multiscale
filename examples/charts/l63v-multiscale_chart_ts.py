import pandas as pd
from toolbox.control import logger
from toolbox.control import handleFiles
from toolbox.control import tools
import matplotlib.pyplot as plt
import seaborn as sns

# paths and parametetes
prefix="l63v-multiscale"
scenario=prefix+"_"+"03"
pathOutputDir="outputs/"+scenario+"/"
pathResources="resources/"
pathOutputFig=pathOutputDir+"fig_01/"

path_sym_emi=pathOutputDir+prefix+"_sym_tra-emi.csv"
path_mat_emi=pathOutputDir+prefix+"_mat_tra-emi.csv"

# setup fig
sns.set_style("whitegrid")
position_color=[2,3,4]
palette=plt.rcParams['axes.prop_cycle'].by_key()['color']

path_sym_sum_ts=pathOutputDir+prefix+"_sym_sum-ts.csv"
path_mat_sum_ts=pathOutputDir+prefix+"_mat_sum-ts.csv"
path_sym_mean_ts=pathOutputDir+prefix+"_sym_mean-ts.csv"
path_mat_mean_ts=pathOutputDir+prefix+"_mat_mean-ts.csv"

path_od= pathOutputDir+"l63v-multiscale_od_matrix_sym.csv"

path_mat_nveh=pathOutputDir+prefix+"_mat_nVeh.csv"
path_sym_nveh=pathOutputDir+prefix+"_sym_nVeh.csv"
path_sym_glob=pathOutputDir+"l63v-multiscale_000000_235959_traf_capteurs_global.csv"


# logger and handleFiles
# ----------------------------------------------------------------------------------------------------------------------
hf=handleFiles.HandleFiles(logger=None)
hf.createDirectories(["outputs",pathOutputDir,pathOutputFig])
logger=logger.Logger(storeLog=True,initStore=True,pathLog=pathOutputDir+prefix+"_log_charts_ts.md")
hf.setLogger(logger=logger)
logger.setDisplay(True,True,True,True)
logger.storeLocal(False)
cwd=hf.getDefCwd()
logger.log(cl=None,method=None,message="start create df for symuvia")

run_od,run_traffic,run_average_speed,run_pollutants,run_vehicles=False,True,False,True,True

# create charts
# ----------------------------------------------------------------------------------------------------------------------
logger.log(cl=None,method=None,message="start create charts ts")

df_sym=pd.read_csv(filepath_or_buffer=path_sym_sum_ts,sep=";")
df_mat=pd.read_csv(filepath_or_buffer=path_mat_sum_ts,sep=";")
df_sym_mean=pd.read_csv(filepath_or_buffer=path_sym_mean_ts,sep=";")
df_mat_mean=pd.read_csv(filepath_or_buffer=path_mat_mean_ts,sep=";")

df_od=pd.read_csv(filepath_or_buffer=path_od,sep=";")
#
# print ("---------------------------- sum sym")
# print (df_sym)
# print (df_sym.describe())
#
# print ("---------------------------- sum mat")
# print (df_mat)
# print (df_mat.describe())
#
# print ("---------------------------- mean sym")
# print (df_sym_mean)
# print (df_sym_mean.describe())
#
# print ("---------------------------- mean mat")
# print (df_mat_mean)
# print (df_mat_mean.describe())

# od
if run_od:
    print ("---------------------------- od")

    df_od["i"]=1
    df_od["ts_pos"]=df_od["creation"]//900
    df_od["ts"]=df_od["ts_pos"]*900

    df_od_sum=df_od.groupby(by=["ts"]).sum()
    print (df_od_sum)
    fig, ax = plt.subplots()
    g=sns.lineplot(data=df_od_sum, x="ts", y="i",color="black")
    sns.scatterplot(data=df_od_sum, x="ts", y="i",color="black")
    ax.set(xlabel='hours [h]', ylabel="number of trips per 15 min [-]")
    plt.xticks([_*60*60 for _ in range(0,25)],list(range(0,25)))

    tools.saveFig(fig=fig,pathSave=cwd+pathOutputFig+"{}_{}.jpg".format(prefix,"od"),logger=logger)

# traffic
if run_traffic:
    print ("---------------------------- traffic")
    list_ind=["td","nVeh"]
    y_labels=['total travel distance [Km]','number of vehicles per time slot of 900s [-]']
    print (df_sym)
    for i in range(len(list_ind)):
        fig, ax = plt.subplots()
        sns.lineplot(data=df_sym, x="ts", y=list_ind[i],label="Symuvia",color=palette[position_color[1]])
        sns.lineplot(data=df_mat, x="ts", y=list_ind[i],label="MATSim",color=palette[position_color[0]])
        ax.set(xlabel='hours [h]', ylabel=y_labels[i])
        plt.xticks([_*60*60 for _ in range(0,25)],list(range(0,25)))
        tools.saveFig(fig=fig,pathSave=cwd+pathOutputFig+"{}_{}_{}_{}.jpg".format(prefix,"traf","ts",list_ind[i]),logger=logger)
        plt.close()

# average speed
# TODO: check av_sp or av_sp_mps
if run_average_speed:
    print ("---------------------------- average speed")
    fig, ax = plt.subplots()
    sns.lineplot(data=df_sym_mean, x="ts", y="av_sp_kph",label="Symuvia",color=palette[position_color[1]])
    sns.lineplot(data=df_mat_mean, x="ts", y="av_sp_kph",label="MATSim",color=palette[position_color[0]])
    ax.set(xlabel='hours [h]', ylabel="average speed [Km/h]")
    plt.xticks([_*60*60 for _ in range(0,25)],list(range(0,25)))
    tools.saveFig(fig=fig,pathSave=cwd+pathOutputFig+"{}_{}_{}_{}.jpg".format(prefix,"traf","ts","av_sp"),logger=logger)
    plt.close()

# pollution
if run_pollutants:
    print ("---------------------------- emissions")
    y_labels=['CO2 [g]',"NOx [g]","PM10 [-]"]
    list_ind=['co2_g', 'nox_g', 'pm10_g']
    for i in range(len(list_ind)):
        fig, ax = plt.subplots()
        sns.lineplot(data=df_sym, x="ts", y="{}_cop".format(list_ind[i]),label="Symuvia Copert",color=palette[position_color[1]],linestyle='--')
        sns.lineplot(data=df_sym, x="ts", y="{}_hbf".format(list_ind[i]),label="Symuvia HBFEA",color=palette[position_color[1]])
        sns.lineplot(data=df_mat, x="ts", y="{}_cop".format(list_ind[i]),label="MATSim Copert",color=palette[position_color[0]],linestyle='--')
        sns.lineplot(data=df_mat, x="ts", y="{}_hbf".format(list_ind[i]),label="MATSim HBFEA",color=palette[position_color[0]])
        ax.set(xlabel='hours [h]', ylabel=y_labels[i])
        plt.xticks([_*60*60 for _ in range(0,25)],list(range(0,25)))
        tools.saveFig(fig=fig,pathSave=cwd+pathOutputFig+"{}_{}_{}_{}.jpg".format(prefix,"poll","ts",list_ind[i]),logger=logger)
        plt.close()

if run_vehicles:
    print ("---------------------------- vehicles")
    logger.log(cl=None,method=None,message="get charts vehicles")
    df_mat=pd.read_csv(filepath_or_buffer=path_mat_nveh,sep=";")
    df_sym=pd.read_csv(filepath_or_buffer=path_sym_nveh,sep=";")
    df_sym_glo=pd.read_csv(filepath_or_buffer=path_sym_glob,sep=";")
    df_mat=df_mat[df_mat["time"]<=24*60*60]
    fig, ax = plt.subplots()
    # sns.lineplot(data=df_sym_glo, x="debut", y="nbveh",label="Symuvia",color=palette[position_color[1]])

    sns.lineplot(data=df_sym, x="time", y="nVeh",label="Symuvia",color=palette[position_color[1]],linewidth=0.8)
    sns.lineplot(data=df_mat, x="time", y="nVeh",label="MATSim",color=palette[position_color[0]],linewidth=0.8)
    ax.set(xlabel='hours [h]', ylabel="number of vehicles per second [-]")
    plt.xticks([_*60*60 for _ in range(0,25)],list(range(0,25)))

    tools.saveFig(fig=fig,pathSave=cwd+pathOutputFig+"{}_{}_{}.jpg".format(prefix,"traffic","nVeh-per-sec"),logger=logger)