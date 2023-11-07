import pandas as pd
import numpy as np
from toolbox.control import logger
from toolbox.control import handleFiles
from toolbox.control import tools
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import timedelta
from datetime import timedelta

# paths and parametetes
prefix="l63v-multiscale"
scenario=prefix+"_"+"02"
pathOutputDir="outputs/"+scenario+"/"
pathResources="resources/"
pathOutputFig=pathOutputDir+"fig_02/"

sns.set_style("whitegrid")
position_color=[2,3,4]
palette=plt.rcParams['axes.prop_cycle'].by_key()['color']

# paths
path_sym_sum_ts=pathOutputDir+prefix+"_sym_sum-ts.csv"
path_mat_sum_ts=pathOutputDir+prefix+"_mat_sum-ts.csv"
path_mat_tap=pathResources+"tap2023_df-matsim"+".csv"


# logger and handleFiles
# ----------------------------------------------------------------------------------------------------------------------
hf=handleFiles.HandleFiles(logger=None)
hf.createDirectories(["outputs",pathOutputDir,pathOutputFig])
logger=logger.Logger(storeLog=True,initStore=True,pathLog=pathOutputDir+prefix+"_log_test.md")
hf.setLogger(logger=logger)
logger.setDisplay(True,True,True,True)
logger.storeLocal(False)
cwd=hf.getDefCwd()
logger.log(cl=None,method=None,message="start create df for MATSim")

minMaxTs=[0,85500]


# create df base
logger.log(cl=None,method=None,message="start create chart test")
# ----------------------------------------------------------------------------------------------------------------------

df_sym=pd.read_csv(filepath_or_buffer=path_sym_sum_ts,sep=";")
df_mat=pd.read_csv(filepath_or_buffer=path_mat_sum_ts,sep=";")
df_mat_tap=pd.read_csv(filepath_or_buffer=path_mat_tap,sep=";")

print (df_sym)
print (df_mat)
print (df_mat_tap)
# df_mat_tap["dtp"]=df_mat_tap["dtp"]/1000

fig, ax = plt.subplots()
sns.lineplot(data=df_sym, x="ts", y="td",label="Symuvia",color=palette[position_color[1]])
sns.lineplot(data=df_mat, x="ts", y="td",label="MATSim",color=palette[position_color[0]])
sns.lineplot(data=df_mat_tap, x="time", y="dtp",label="MATSim TAP",color=palette[position_color[2]])

# ax.set(xlabel='hours [h]', ylabel=y_labels[i])
plt.xticks([_*60*60 for _ in range(0,25)],list(range(0,25)))
tools.saveFig(fig=fig,pathSave=cwd+pathOutputFig+"{}_{}_{}_{}.jpg".format(prefix,"traf","ts","test_tap"),logger=logger)
plt.close()