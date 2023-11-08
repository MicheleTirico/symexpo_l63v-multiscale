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
pathOutputFig=pathOutputDir+"fig_hist/"

path_trip_sym=pathOutputDir+prefix+"_sym_trips.csv"
path_trip_mat=pathOutputDir+prefix+"_mat_trips.csv"

path_sym_emi=pathOutputDir+prefix+"_sym_tra-emi.csv"
path_mat_emi=pathOutputDir+prefix+"_mat_tra-emi.csv"

# setup fig
sns.set_style("whitegrid")
position_color=[2,3,4]
palette=plt.rcParams['axes.prop_cycle'].by_key()['color']

# logger and handleFiles
# ----------------------------------------------------------------------------------------------------------------------
hf=handleFiles.HandleFiles(logger=None)
hf.createDirectories(["outputs",pathOutputDir,pathOutputFig])
logger=logger.Logger(storeLog=True,initStore=True,pathLog=pathOutputDir+prefix+"_log_charts_hist.md")
hf.setLogger(logger=logger)
logger.setDisplay(True,True,True,True)
logger.storeLocal(False)
cwd=hf.getDefCwd()
logger.log(cl=None,method=None,message="start create df for symuvia")

run_trip,run_hist_traffic=True,True

# create charts
# ----------------------------------------------------------------------------------------------------------------------
logger.log(cl=None,method=None,message="start create charts hist")

# trip
if run_trip:
    print ("---------------------------- trip")
    df_mat=pd.read_csv(filepath_or_buffer=path_trip_mat,sep=";")
    df_sym=pd.read_csv(filepath_or_buffer=path_trip_sym,sep=";")
    bins=50
    alpha=.5
    quantile=1.0
    log_scale=False
    list_x_label=['average length trip [m]',"average time trip [s]"]
    list_hist=["td","ttt"]
    for i in range(len(list_hist)):
        df1_mat=df_mat[["trip_id",list_hist[i]]]
        df1_mat.insert(loc=2,column="model",value="MATSim")
        df1_sym=df_sym[["trip_id",list_hist[i]]]
        df1_sym.insert(loc=2,column="model",value="Symuvia")
        df1_sym=df1_sym[df1_sym[list_hist[i]]<df1_sym[list_hist[i]].quantile(quantile)]
        df1_mat=df1_mat[df1_mat[list_hist[i]]<df1_mat[list_hist[i]].quantile(quantile)]
        df1=pd.concat([df1_mat,df1_sym]).reset_index()
        df1=df1[df1[list_hist[i]]>=0]

        fig, ax = plt.subplots()
        ax.set(xlabel=list_x_label[i], ylabel="probability")
        sns.histplot(data=df1, x=list_hist[i],hue="model", multiple="stack",log_scale=log_scale,alpha=alpha,bins=bins,palette=[palette[position_color[0]],palette[position_color[1]]],stat="probability")
        tools.saveFig(fig=fig,pathSave=cwd+pathOutputFig+"{}_{}_{}_quant-{}_log-{}.jpg".format(prefix,"trip_hist",list_hist[i],quantile,log_scale),logger=logger)
        plt.close()

if run_hist_traffic:
    print ("---------------------------- traffic")
    df_mat=pd.read_csv(filepath_or_buffer=path_mat_emi,sep=";")
    df_sym=pd.read_csv(filepath_or_buffer=path_sym_emi,sep=";")
    bins=50
    alpha=.5
    quantile=1.0
    log_scale=False
    list_hist=["nVeh","av_sp_kph","td"]
    list_x_label=['number of vehicles [-]',"average speed [KM/h]","total travel distance [m]"]
    for i in range(len(list_hist)):
        df1_mat=df_mat[["id_link",list_hist[i]]]
        df1_mat.insert(loc=2,column="model",value="MATSim")
        df1_sym=df_sym[["id_link",list_hist[i]]]
        df1_sym.insert(loc=2,column="model",value="Symuvia")
        df1_sym=df1_sym[df1_sym[list_hist[i]]<df1_sym[list_hist[i]].quantile(quantile)]
        df1_mat=df1_mat[df1_mat[list_hist[i]]<df1_mat[list_hist[i]].quantile(quantile)]
        df1=pd.concat([df1_mat,df1_sym]).reset_index()
        df1=df1[df1[list_hist[i]]>=0]

        fig, ax = plt.subplots()
        ax.set(xlabel=list_x_label[i], ylabel="probability")
        sns.histplot(data=df1, x=list_hist[i],hue="model", multiple="stack",log_scale=log_scale,alpha=alpha,bins=bins,palette=[palette[position_color[0]],palette[position_color[1]]],stat="probability")
        tools.saveFig(fig=fig,pathSave=cwd+pathOutputFig+"{}_{}_{}_quant-{}_log-{}.jpg".format(prefix,"traf_hist",list_hist[i],quantile,log_scale),logger=logger)
        plt.close()

