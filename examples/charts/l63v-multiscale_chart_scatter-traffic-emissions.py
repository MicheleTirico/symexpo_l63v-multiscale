import pandas as pd
from toolbox.control import logger
from toolbox.control import handleFiles
from toolbox.control import tools
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Polygon

# paths and parametetes
prefix="l63v-multiscale"
scenario=prefix+"_"+"02"
pathOutputDir="outputs/"+scenario+"/"
pathResources="resources/"
pathOutputFig=pathOutputDir+"fig_04/"

# setup fig
sns.set_style("whitegrid")
position_color=[2,3,4]
palette=plt.rcParams['axes.prop_cycle'].by_key()['color']

path_sym_sum_ts=pathOutputDir+prefix+"_sym_sum-ts.csv"
path_mat_sum_ts=pathOutputDir+prefix+"_mat_sum-ts.csv"
path_sym_mean_ts=pathOutputDir+prefix+"_sym_mean-ts.csv"
path_mat_mean_ts=pathOutputDir+prefix+"_mat_mean-ts.csv"

# logger and handleFiles
# ----------------------------------------------------------------------------------------------------------------------
hf=handleFiles.HandleFiles(logger=None)
hf.createDirectories(["outputs",pathOutputDir,pathOutputFig])
logger=logger.Logger(storeLog=True,initStore=True,pathLog=pathOutputDir+prefix+"_log_charts_scatter-traffic-emissions.md")
hf.setLogger(logger=logger)
logger.setDisplay(True,True,True,True)
logger.storeLocal(False)
cwd=hf.getDefCwd()
logger.log(cl=None,method=None,message="start create df for symuvia")

run_scatter,run_scatter_standard=True,True

list_traffic=["td","nVeh"]
list_pol=['co2_g_cop','nox_g_cop', 'pm10_g_cop','co2_g_hbf', 'nox_g_hbf', 'pm10_g_hbf']

x_label=["total travel distance [m]", "number of vehicles [-]"]
y_label=["CO2 Copert [g]", "NOx Copert [g]", "PM10 Copert [-]","CO2 HBEFA [g]", "NOx HBEFA [g]", "PM10 HBEFA [-]"]

# create charts
# ----------------------------------------------------------------------------------------------------------------------
logger.log(cl=None,method=None,message="start create charts scatterplot traffic vs emissions")

# scatter
if run_scatter:
    print ("---------------------------- scatter")
    df_sym=pd.read_csv(filepath_or_buffer=path_sym_sum_ts,sep=";")
    df_mat=pd.read_csv(filepath_or_buffer=path_mat_sum_ts,sep=";")
    df_sym_mean=pd.read_csv(filepath_or_buffer=path_sym_mean_ts,sep=";")
    df_mat_mean=pd.read_csv(filepath_or_buffer=path_mat_mean_ts,sep=";")
    for tr in range(len(list_traffic)):
        for pol in range(len(list_pol)):
            fig, ax = plt.subplots()
            sns.scatterplot(data=df_sym, x=list_traffic[tr],y=list_pol[pol],color=palette[position_color[1]],label="Symuvia",size="ts",legend=False)
            sns.scatterplot(data=df_mat, x=list_traffic[tr],y=list_pol[pol],color=palette[position_color[0]],label="MATSim",size="ts",legend=False)
            ax.set(xlabel=x_label[tr], ylabel=y_label[pol])

            coordinates=[]
            for i in range(len(list(df_mat[list_traffic[tr]]))):     coordinates.append([list(df_mat[list_traffic[tr]])[i],list(df_mat[list_pol[pol]])[i]      ])
            p = Polygon(coordinates, facecolor = 'k',alpha=0.5,color=palette[position_color[0]],fill=False)
            ax.add_patch(p)
            coordinates=[]
            for i in range(len(list(df_sym[list_traffic[tr]]))):     coordinates.append([list(df_sym[list_traffic[tr]])[i],list(df_sym[list_pol[pol]])[i]      ])
            p = Polygon(coordinates, facecolor = 'k',alpha=0.5,color=palette[position_color[1]],fill=False)
            ax.add_patch(p)

            ax.legend()
            tools.saveFig(fig=fig,pathSave=cwd+pathOutputFig+"{}_{}_{}_{}.jpg".format(prefix,"scat-tr-emi",list_traffic[tr],list_pol[pol]),logger=logger)
            plt.close()

    for pol in range(len(list_pol)):
        fig, ax = plt.subplots()
        sns.scatterplot(data=df_sym_mean, x="av_sp_kph",y=list_pol[pol],color=palette[position_color[1]],label="Symuvia",size="ts",legend=False)
        sns.scatterplot(data=df_mat_mean, x='av_sp_kph',y=list_pol[pol],color=palette[position_color[0]],label="MATSim",size="ts",legend=False)
        ax.set(xlabel="average speed [Km/h]", ylabel=y_label[pol])

        coordinates=[]
        for i in range(len(list(df_mat_mean["av_sp_kph"]))):     coordinates.append([list(df_mat_mean["av_sp_kph"])[i],list(df_mat_mean[list_pol[pol]])[i]      ])
        p = Polygon(coordinates, facecolor = 'k',alpha=0.5,color=palette[position_color[0]],fill=False)
        ax.add_patch(p)
        coordinates=[]
        for i in range(len(list(df_sym_mean["av_sp_kph"]))):     coordinates.append([list(df_sym_mean["av_sp_kph"])[i],list(df_sym_mean[list_pol[pol]])[i]      ])
        p = Polygon(coordinates, facecolor = 'k',alpha=0.5,color=palette[position_color[1]],fill=False)
        ax.add_patch(p)

        ax.legend()
        tools.saveFig(fig=fig,pathSave=cwd+pathOutputFig+"{}_{}_{}_{}.jpg".format(prefix,"scat-tr-emi","av_sp_kph",list_pol[pol]),logger=logger)

        plt.close()

# standard
if run_scatter_standard:
    print ("---------------------------- standard")
    df_sym=pd.read_csv(filepath_or_buffer=path_sym_sum_ts,sep=";")
    df_mat=pd.read_csv(filepath_or_buffer=path_mat_sum_ts,sep=";")
    df_sym_mean=pd.read_csv(filepath_or_buffer=path_sym_mean_ts,sep=";")
    df_mat_mean=pd.read_csv(filepath_or_buffer=path_mat_mean_ts,sep=";")

    list_col=list_pol+list_traffic
    for a in list_col:
        for df in [df_sym,df_mat]:  df[a] = (df[a] - df[a].mean()) / df[a].std()

    for a in ["av_sp_kph"]+list_pol:
        for df in [df_sym_mean,df_mat_mean]:  df[a] = (df[a] - df[a].mean()) / df[a].std()

    for tr in range(len(list_traffic)):
        for pol in range(len(list_pol)):
            fig, ax = plt.subplots()
            sns.scatterplot(data=df_sym, x=list_traffic[tr],y=list_pol[pol],color=palette[position_color[1]],label="Symuvia",size="ts",legend=False)
            sns.scatterplot(data=df_mat, x=list_traffic[tr],y=list_pol[pol],color=palette[position_color[0]],label="MATSim",size="ts",legend=False)

            coordinates=[]
            for i in range(len(list(df_mat[list_traffic[tr]]))):     coordinates.append([list(df_mat[list_traffic[tr]])[i],list(df_mat[list_pol[pol]])[i]      ])
            p = Polygon(coordinates, facecolor = 'k',alpha=0.5,color=palette[position_color[0]],fill=False)
            ax.add_patch(p)
            coordinates=[]
            for i in range(len(list(df_sym[list_traffic[tr]]))):     coordinates.append([list(df_sym[list_traffic[tr]])[i],list(df_sym[list_pol[pol]])[i]      ])
            p = Polygon(coordinates, facecolor = 'k',alpha=0.5,color=palette[position_color[1]],fill=False)
            ax.add_patch(p)

            ax.set(xlabel="standard "+x_label[tr], ylabel="standard "+y_label[pol])
            ax.legend()
            tools.saveFig(fig=fig,pathSave=cwd+pathOutputFig+"{}_{}_{}_{}_std.jpg".format(prefix,"scat-tr-emi",list_traffic[tr],list_pol[pol]),logger=logger)
            plt.close()

    for pol in range(len(list_pol)):
        fig, ax = plt.subplots()
        sns.scatterplot(data=df_sym_mean, x="av_sp_kph",y=list_pol[pol],color=palette[position_color[1]],label="Symuvia",size="ts",legend=False)
        sns.scatterplot(data=df_mat_mean, x='av_sp_kph',y=list_pol[pol],color=palette[position_color[0]],label="MATSim",size="ts",legend=False)
        ax.set(xlabel="standard "+"average speed [Km/h]", ylabel="standard "+y_label[pol])

        coordinates=[]
        for i in range(len(list(df_mat_mean["av_sp_kph"]))):     coordinates.append([list(df_mat_mean["av_sp_kph"])[i],list(df_mat_mean[list_pol[pol]])[i]      ])
        p = Polygon(coordinates, facecolor = 'k',alpha=0.5,color=palette[position_color[0]],fill=False)
        ax.add_patch(p)
        coordinates=[]
        for i in range(len(list(df_sym_mean["av_sp_kph"]))):     coordinates.append([list(df_sym_mean["av_sp_kph"])[i],list(df_sym_mean[list_pol[pol]])[i]      ])
        p = Polygon(coordinates, facecolor = 'k',alpha=0.5,color=palette[position_color[1]],fill=False)
        ax.add_patch(p)


        ax.legend()
        tools.saveFig(fig=fig,pathSave=cwd+pathOutputFig+"{}_{}_{}_{}_std.jpg".format(prefix,"scat-tr-emi","av_sp_kph",list_pol[pol]),logger=logger)
        plt.close()