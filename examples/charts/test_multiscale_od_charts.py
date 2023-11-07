import pandas as pd
import numpy as np
from toolbox.control import logger
from toolbox.control import handleFiles
from toolbox.control import tools

import matplotlib.pyplot as plt
import seaborn as sns

# paths and parametetes
prefix="l63v-multiscale"
scenario=prefix+"_"+"01"
pathOutputDir="outputs/"+scenario+"/"
pathResources="resources/"
pathOutputFig=pathOutputDir+"fig/"

# files to set
path_od= pathOutputDir+"l63v-multiscale_od_matrix_sym.csv"

# logger and handleFiles
# ----------------------------------------------------------------------------------------------------------------------
hf=handleFiles.HandleFiles(logger=None)
hf.createDirectories([pathOutputDir,pathOutputFig])
logger=logger.Logger(storeLog=True,initStore=True,pathLog="outputs/"+scenario+"/"+prefix+"_log_test.md")
hf.setLogger(logger=logger)
logger.setDisplay(True,True,True,True)
logger.storeLocal(False)
cwd=hf.getDefCwd()
logger.log(cl=None,method=None,message="start test")

df_od=pd.read_csv(filepath_or_buffer=path_od,sep=";")
df_od["i"]=1
df_od["ts"]=df_od["creation"]//900

df_od_sum=df_od.groupby(by=["ts"]).sum()
fig, ax = plt.subplots()
g=sns.lineplot(data=df_od_sum, x="ts", y="i",label="Symuvia")
sns.scatterplot(data=df_od_sum, x="ts", y="i",label="Symuvia")
tools.saveFig(fig=fig,pathSave=cwd+pathOutputFig+"{}_{}_{}.jpg".format(prefix,"od","nVeh"),logger=logger)

plt.close()