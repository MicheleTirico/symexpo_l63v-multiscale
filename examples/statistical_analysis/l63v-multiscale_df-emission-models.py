import pandas as pd
import numpy as np
from toolbox.control import logger
from toolbox.control import handleFiles
from toolbox.control import tools

# paths and parametetes
prefix="l63v-multiscale"
scenario=prefix+"_"+"02"
pathOutputDir="outputs/"+scenario+"/"
pathResources="resources/"
pathOutputFig=pathOutputDir+"fig/"

# path
path_df_co2=pathResources+"copert_alex/"+"COPERT_C5_Légers_CO2.csv"
path_df_nox=pathResources+"copert_alex/"+"COPERT_C5_Légers_NOX.csv"
path_df_pm10=pathResources+"copert_alex/"+"COPERT_C5_Légers_PM10.csv"
path_out_merged=pathOutputDir+prefix+"_copert.csv"

path_complet=pathResources+"FE_HBEFA_TAP23_complet.csv"
path_ts=pathResources+"HBEFA_TS.csv"
path_hbf_fe=pathOutputDir+prefix+"_hbfea.csv"

run_cop,run_hbf=False,True
# logger and handleFiles
# ----------------------------------------------------------------------------------------------------------------------
hf=handleFiles.HandleFiles(logger=None)
hf.createDirectories([pathOutputDir,pathOutputFig])
logger=logger.Logger(storeLog=True,initStore=True,pathLog="outputs/"+scenario+"/"+prefix+"_log_get-df-emission-models.md")
hf.setLogger(logger=logger)
logger.setDisplay(True,True,True,True)
logger.storeLocal(False)
cwd=hf.getDefCwd()

# ----------------------------------------------------------------------------------------------------------------------
if run_cop:
    logger.log(cl=None,method=None,message="start create dataframe copert")
    df1=pd.read_csv(filepath_or_buffer=path_df_co2,sep=";")
    df2=pd.read_csv(filepath_or_buffer=path_df_nox,sep=";")
    df3=pd.read_csv(filepath_or_buffer=path_df_pm10,sep=";")

    df1.rename(columns={"Emission (g/km)":"co2_g/km"},inplace=True)
    df2.rename(columns={"Emission (g/km)":"nox_g/km"},inplace=True)
    df3.rename(columns={"Emission (g/km)":"pm10_g/km"},inplace=True)

    df4=pd.merge(df1,df2,left_on="speedInKph",right_on="speedInKph",how="left")
    df4=pd.merge(df4,df3,left_on="speedInKph",right_on="speedInKph",how="left")

    tools.storeDataframe(logger=logger,pathStore=path_out_merged,df=df4)                                                    # store df
    logger.log(cl=None,method=None,message="finish create dataframe copert")

# ----------------------------------------------------------------------------------------------------------------------
if run_hbf:
    logger.log(cl=None,method=None,message="start create dataframe HBEFA")
    df_complet=pd.read_csv(filepath_or_buffer=path_complet,sep=";")
    df_ts=pd.read_csv(filepath_or_buffer=path_ts,sep=";")
    df1=pd.merge(df_complet,df_ts,left_on="TrafficSit",right_on="TS_fr",how="inner")
    df1=df1[tools.dropValColumns(columns=list(df1.columns),listValToDrop=['TrafficSit'])]
    df1=df1.rename(columns={"TS":"ts_en","TS_fr":"ts_fr"})

    print (df1)
    tools.storeDataframe(logger=logger,pathStore=path_hbf_fe,df=df1)                                                    # store df
    logger.log(cl=None,method=None,message="finish create dataframe HBFEA")