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
pathOutputFig=pathOutputDir+"fig_04/"

# files to set
path_mat_emissions=pathOutputDir+"l63v-multiscale_mat_df-tra.csv"
path_hbf_trad=pathResources+"HBEFA_TS.csv"
path_hbf_level=pathResources+"TS_HBEFA_TAP23.csv"
path_hbf_emission_factor=pathResources+"FE_HBEFA_TAP23_complet.csv"
path_mat_level=pathOutputDir+prefix+"_test_mat_hbf_level.csv"
path_mat_hbf_emissions=pathOutputDir+prefix+"_test_mat-hbf-links.csv"
path_mat_test_hbf_sum=pathOutputDir+prefix+"_test_mat-hbf-sum.csv"
path_mat_test_hbf_mean=pathOutputDir+prefix+"_test_mat-hbf-mean.csv"

# parameters
run_compute_level,run_compute_emission,run_sum=False,True,True

# logger and handleFiles
# ----------------------------------------------------------------------------------------------------------------------
hf=handleFiles.HandleFiles(logger=None)
hf.createDirectories([pathOutputDir,pathOutputFig])
logger=logger.Logger(storeLog=True,initStore=True,pathLog="outputs/"+scenario+"/"+prefix+"_log_mat-hbf-lin.md")
hf.setLogger(logger=logger)
logger.setDisplay(True,True,True,True)
logger.storeLocal(False)
cwd=hf.getDefCwd()
logger.log(cl=None,method=None,message="start compute emission matsim hbefa")

# merge df
# ----------------------------------------------------------------------------------------------------------------------
# import df
df_mat=pd.read_csv(filepath_or_buffer=path_mat_emissions,sep=";")
df_hbf_trad=pd.read_csv(filepath_or_buffer=path_hbf_trad,sep=";")
df_hbf_lev=pd.read_csv(filepath_or_buffer=path_hbf_level,sep=";",decimal=",")
df_emission_factor=pd.read_csv(filepath_or_buffer=path_hbf_emission_factor,sep=";")


# get English and French triplet, and level
df_hbf_trad["triplet_en"]=df_hbf_trad["TS"].str.split("/",expand=True)[0]+"/"+df_hbf_trad["TS"].str.split("/",expand=True)[1]+"/"+df_hbf_trad["TS"].str.split("/",expand=True)[2]
df_hbf_trad["triplet_fr"]=df_hbf_trad["TS_fr"].str.split("/",expand=True)[0]+"/"+df_hbf_trad["TS_fr"].str.split("/",expand=True)[1]+"/"+df_hbf_trad["TS_fr"].str.split("/",expand=True)[2]
# df_hbf_trad["level"]=df_hbf_trad["TS"].str.split("/",expand=True)[3]

df_hbf_trad=df_hbf_trad[["triplet_en","triplet_fr"]].drop_duplicates()

# add triplet to links
df_mat=pd.merge(df_mat,df_hbf_trad,left_on="type",right_on="triplet_en",how="inner")
# tools.storeDataframe(logger=logger,pathStore=path_test_01,df=df_mat)
df_mat["triplet_fr"] = df_mat["triplet_fr"].replace('Autor-Nat.','Autor-Urb', regex=True)

# compute traffic level
df_mat_level=None
if run_compute_level:
    level=['/Fluide','/Dense','/Saturé','/Congestion','/Congestion2']
    ss=[]

    # df_mat=df_mat[0:-1]
    for i in range(len(df_mat)):
        # print (i)
        try:
            if df_mat.av_sp_kph[i] < float(df_hbf_lev.V[df_hbf_lev.TrafficSit==df_mat.triplet_fr[i]+level[4]]):
                ss.append(df_mat.triplet_fr[i]+level[4])
            elif df_mat.av_sp_kph[i] < float(df_hbf_lev[df_hbf_lev.TrafficSit==df_mat.triplet_fr[i]+level[3]].V):
                ss.append(df_mat.triplet_fr[i]+level[3])
            elif df_mat.av_sp_kph[i] < float(df_hbf_lev[df_hbf_lev.TrafficSit==df_mat.triplet_fr[i]+level[2]].V):
                ss.append(df_mat.triplet_fr[i]+level[2])
            elif df_mat.av_sp_kph[i] < float(df_hbf_lev[df_hbf_lev.TrafficSit==df_mat.triplet_fr[i]+level[1]].V):
                ss.append(df_mat.triplet_fr[i]+level[1])
            else:
                ss.append(df_mat.triplet_fr[i]+level[0])
        except TypeError:
            print (i,df_mat.av_sp_kph[i],df_mat.type[i],df_mat.triplet_fr[i])
    df_mat_level = df_mat.assign(TrafficSit = ss)
    tools.storeDataframe(logger=logger,pathStore=path_mat_level,df=df_mat_level)

if run_compute_emission:
    df_links_level_fe=pd.read_csv(filepath_or_buffer=path_mat_level,sep=";")
    df_hbefa_ef=pd.read_csv(filepath_or_buffer=path_hbf_emission_factor,sep=";")

    # merge df
    df_links_poll=pd.merge(df_links_level_fe,df_hbefa_ef,left_on="TrafficSit",right_on="TrafficSit")

    # compute values for links
    df_links_poll["poll"]=df_links_poll["EFA_weighted"]*df_links_poll["td"] /1000 #  ??????????????????

    components=df_links_poll["Component"].unique()
    components=["NOx","PM (non-exhaust)", "CO2(rep)"]
    p=df_links_poll["ts"].unique()

    df_final=pd.DataFrame()
    df_final["id_link"]=df_links_poll["id_link"]
    df_final["ts"]=df_links_poll["ts"]
    df_final["td"]=df_links_poll["td"]
    df_final["length"]=df_links_poll["length"]
    df_final['nVeh']=df_links_poll['nVeh']
    df_final['av_sp_kph']=df_links_poll['av_sp_kph']
    print (df_links_poll.columns)


    for component in components:
        logger.log(cl=None,method=None,message="compute emissions for pollutant: {}".format(component))
        df1=df_links_poll[df_links_poll["Component"]==component]
        df1=df1[["poll","ts","id_link"]]
        df1.rename(columns = {'poll':component}, inplace = True)
        df_final=pd.merge(df_final,df1,left_on=["id_link","ts"],right_on=["id_link","ts"],how="inner")

    df_final=df_final.drop_duplicates()#subset=["id_link","ts"])

    print (df_final)
    tools.storeDataframe(logger=logger,pathStore=path_mat_hbf_emissions,df=df_final)

if run_sum:

    df_final=pd.read_csv(filepath_or_buffer=path_mat_hbf_emissions,sep=";")
    # print (df_final)
    df_final=df_final.rename(columns={"NOx":"nox_g_hbf","PM (non-exhaust)":"pm10_g_hbf", "CO2(rep)":"co2_g_hbf" })

    # df1=df_final[tools.dropValColumns(columns=list(df_final.columns),listValToDrop=['Unnamed: 0', "id_link"])]

    df1=df_final.groupby(by="ts").sum().reset_index()
    print (df1[df1["ts"]==28800])
    # print (df1)
    tools.storeDataframe(logger=logger,pathStore=path_mat_test_hbf_sum,df=df1)


    df1=df_final[tools.dropValColumns(columns=list(df_final.columns),listValToDrop=['Unnamed: 0', "id_link"])]
    df1=df_final.groupby(by="ts").mean().reset_index()
    print (df1[df1["ts"]==28800])
    # print (df1)
    tools.storeDataframe(logger=logger,pathStore=path_mat_test_hbf_mean,df=df1)