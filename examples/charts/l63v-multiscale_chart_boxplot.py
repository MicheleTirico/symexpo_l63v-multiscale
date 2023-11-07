import pandas as pd
from toolbox.control import logger
from toolbox.control import handleFiles
from toolbox.control import tools
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import timedelta


# paths and parametetes
prefix="l63v-multiscale"
scenario=prefix+"_"+"03"
pathOutputDir="outputs/"+scenario+"/"
pathResources="resources/"
pathOutputFig=pathOutputDir+"fig_boxplot_01/"

# setup fig
sns.set_style("whitegrid")
position_color=[2,3,4]
palette=plt.rcParams['axes.prop_cycle'].by_key()['color']

path_sym_emi=pathOutputDir+prefix+"_sym_tra-emi.csv"
path_mat_emi=pathOutputDir+prefix+"_mat_tra-emi.csv"

path_sym_selected=pathOutputDir+prefix+"_sym_selected.csv"
path_mat_selected=pathOutputDir+prefix+"_mat_selected.csv"

def _get_list_labels (list_sec):
    list_labels=[]
    for sec in list_sec:
        x = str(timedelta(seconds=sec)).split(':')
        list_labels.append("{}:{}".format(x[0],x[1]))
    return list_labels

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

run_all,run_selected=False,True

# create charts
# ----------------------------------------------------------------------------------------------------------------------
logger.log(cl=None,method=None,message="start create charts ts")

list_ind=['av_sp_mps', 'nVeh', 'td',  'co2_g_cop','nox_g_cop', 'pm10_g_cop', 'nox_g_hbf', 'co2_g_hbf','pm10_g_hbf']

minMaxTs=[0,10*60*60]
if run_all:
    df_sym=pd.read_csv(filepath_or_buffer=path_sym_emi,sep=";")
    df_mat=pd.read_csv(filepath_or_buffer=path_mat_emi,sep=";")
    logger.log(cl=None,method=None,message="start create boxplot all ")
    for i in range(len(list_ind)):
        df1_mat=df_mat[["ts",list_ind[i]]]
        df1_mat.insert(loc=2,column="model",value="MATSim")
        df1_sym=df_sym[["ts",list_ind[i]]]
        df1_sym.insert(loc=2,column="model",value="Symuvia")
        df1=pd.concat([df1_mat,df1_sym])
        quantile=1.0
        df1=df1[df1[list_ind[i]]<df1[list_ind[i]].quantile(quantile)]
        df1=df1[df1["ts"]>=minMaxTs[0]]
        df1=df1[df1["ts"]<=minMaxTs[1]]
        df1=df1.reset_index()
        fig, ax = plt.subplots()
        g=sns.boxplot(data=df1, x="ts",y=list_ind[i],hue="model",palette=[palette[position_color[0]],palette[position_color[1]]],fliersize=1)
        ax.legend(loc='upper right')
        ax.set(xlabel='time slots 900s [h:mm]', ylabel=list_ind[i])
        # plt.xticks([_*60*60 for _ in range(0,25)],list(range(0,25)))

        list_labels=_get_list_labels(list_sec=[_*900 for _ in range(minMaxTs[0],minMaxTs[1] )])
        g.set_xticklabels(list_labels,rotation=45)
        tools.saveFig(fig=fig,pathSave=cwd+pathOutputFig+"{}_{}_{}_{}.jpg".format(prefix,"traf","boxplot",list_ind[i]),logger=logger)
        plt.close()

# pollution
if run_selected:
    logger.log(cl=None,method=None,message="start create boxplot selected scenarios ")
    df_sym=pd.read_csv(filepath_or_buffer=path_sym_selected,sep=";")
    df_mat=pd.read_csv(filepath_or_buffer=path_mat_selected,sep=";")
    scenarios=["6:00","8:00","9:30","15:00","17:30","22:00"]
    scenarios_sec=[tools.get_second(_) for _ in scenarios]
    fig, ax = plt.subplots()
    for i in range(len(list_ind)):
        df1_mat=df_mat[["ts",list_ind[i]]]
        df1_mat.insert(loc=2,column="model",value="MATSim")
        df1_sym=df_sym[["ts",list_ind[i]]]
        df1_sym.insert(loc=2,column="model",value="Symuvia")
        df1=pd.concat([df1_mat,df1_sym])
        quantile=1.0
        df1=df1[df1[list_ind[i]]<df1[list_ind[i]].quantile(quantile)]
        df1=df1.reset_index()
        fig, ax = plt.subplots()
        g=sns.boxplot(data=df1, x="ts",y=list_ind[i],hue="model",palette=[palette[position_color[0]],palette[position_color[1]]],fliersize=1)
        ax.legend(loc='upper right')
        ax.set(xlabel='time slots 900s [h:mm]', ylabel=list_ind[i])
        # plt.xticks([_*60*60 for _ in range(0,25)],list(range(0,25)))

        g.set_xticklabels(scenarios,rotation=0)
        tools.saveFig(fig=fig,pathSave=cwd+pathOutputFig+"{}_{}_{}_{}_{}.jpg".format(prefix,"traf","boxplot",list_ind[i],"scenarios"),logger=logger)
        plt.close()



