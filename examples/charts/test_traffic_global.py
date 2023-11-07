from ctypes import cdll, byref
import ctypes as ct
import os
import pandas as pd
import datetime
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
pathOutputFig=pathOutputDir+"fig/"

# files to set
path_od= pathOutputDir+"l63v-multiscale_od_matrix_sym.csv"
path_sym_traffic=pathOutputDir+"l63v-multiscale_000000_235959_traf_capteurs_global.csv"
# logger and handleFiles
# ----------------------------------------------------------------------------------------------------------------------
hf=handleFiles.HandleFiles(logger=None)
hf.createDirectories(["outputs",pathOutputDir,pathOutputFig])
logger=logger.Logger(storeLog=True,initStore=True,pathLog=pathOutputDir+prefix+"_log_test.md")
hf.setLogger(logger=logger)
logger.setDisplay(True,True,True,True)
logger.storeLocal(False)
cwd=hf.getDefCwd()
logger.log(cl=None,method=None,message="start run test")

# ----------------------------------------------------------------------------------------------------------------------
df_sym=pd.read_csv(filepath_or_buffer=path_sym_traffic,sep=";")
# df_sym=df_sym[tools.dropValColumns(columns=list(df_sym.columns),listValToDrop=["id"])]
columns=list(df_sym.columns)
print (columns)
print (df_sym)


for i in ['distance_totale_parcourue', 'nbveh', 'temps_total_passe', 'vit']:
    fig, ax = plt.subplots()
    g=sns.lineplot(data=df_sym, x="debut", y=i,label="Symuvia")
    sns.scatterplot(data=df_sym, x="debut", y=i,label="Symuvia")

    tools.saveFig(fig=fig,pathSave=cwd+pathOutputFig+"{}_{}_{}.jpg".format(prefix,"traffic_global",i),logger=logger)
    plt.close()


