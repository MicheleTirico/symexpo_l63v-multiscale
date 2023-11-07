import pandas as pd
from toolbox.control import logger
from toolbox.control import handleFiles
from toolbox.control import tools
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# paths and parametetes
prefix="l63v-multiscale"
scenario=prefix+"_"+"03"
pathOutputDir="outputs/"+scenario+"/"
pathResources="resources/"
pathOutputFig=pathOutputDir+"fig/"

path_sym_traffic=pathOutputDir+"l63v-multiscale_000000_235959_traf_capteurs_global.csv"

path_mat_tra=pathOutputDir+prefix+"_mat_df-tra.csv"

# logger and handleFiles
# ----------------------------------------------------------------------------------------------------------------------
hf=handleFiles.HandleFiles(logger=None)
hf.createDirectories(["outputs",pathOutputDir,pathOutputFig])
logger=logger.Logger(storeLog=True,initStore=True,pathLog=pathOutputDir+prefix+"_log_test.md")
hf.setLogger(logger=logger)
logger.setDisplay(True,True,True,True)
logger.storeLocal(False)
cwd=hf.getDefCwd()
logger.log(cl=None,method=None,message="start test")

df_mat=pd.read_csv(filepath_or_buffer=path_mat_tra,sep=";")
df1=df_mat.groupby(by=["ts"]).sum().reset_index()

df_sym=pd.read_csv(filepath_or_buffer=path_sym_traffic,sep=";")



fig, ax = plt.subplots()
sns.lineplot(data=df1, x="ts", y="td",label="MATSim")
sns.lineplot(data=df_sym, x="debut", y="distance_totale_parcourue",label="Symuvia")
plt.xticks([_*60*60 for _ in range(0,25)],list(range(0,25)))
tools.saveFig(fig=fig,pathSave=cwd+pathOutputFig+"{}_{}_{}.jpg".format(prefix,"test","td2"),logger=logger)
plt.close()


fig, ax = plt.subplots()
sns.lineplot(data=df1, x="ts", y="nVeh",label="MATSim")
sns.lineplot(data=df_sym, x="debut", y="nbveh",label="Symuvia")
plt.xticks([_*60*60 for _ in range(0,25)],list(range(0,25)))
tools.saveFig(fig=fig,pathSave=cwd+pathOutputFig+"{}_{}_{}.jpg".format(prefix,"test","nVeh"),logger=logger)
plt.close()