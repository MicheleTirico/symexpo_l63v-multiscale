import pandas as pd
from toolbox.control import logger
from toolbox.control import handleFiles
from toolbox.control import tools
import numpy as np

# paths and parametetes
prefix="l63v-multiscale"
scenario=prefix+"_"+"03"
pathOutputDir="outputs/"+scenario+"/"
pathResources="resources/"
pathOutputFig=pathOutputDir+"fig/"

# paths
path_copert=pathOutputDir+prefix+"_copert"+".csv"
path_mat_tra=pathOutputDir+prefix+"_mat_df-tra.csv"
path_mat_cop=pathOutputDir+prefix+"_mat_df-tra-cop.csv"

path_hbf=pathOutputDir+prefix+"_hbfea.csv"
path_links=pathOutputDir+prefix+"_mat_links.csv"
path_hbf_level=pathResources+"TS_HBEFA_TAP23.csv"
path_mat_level=pathOutputDir+prefix+"_mat_hbf_level.csv"
path_hbf_fe=pathOutputDir+prefix+"_hbfea.csv"
path_mat_hbf=pathOutputDir+prefix+"_mat_df-hbf.csv"
path_mat_emi=pathOutputDir+prefix+"_mat_tra-emi.csv"
path_mat_traffic=pathResources+"tap2023_network_matsim_length"+".csv"
path_hbf_trad=pathResources+"HBEFA_TS.csv"
path_hbf_emission_factor=pathResources+"FE_HBEFA_TAP23_complet.csv"

path_mat_sum_ts=pathOutputDir+prefix+"_mat_sum-ts.csv"
path_mat_sum_link=pathOutputDir+prefix+"_mat_sum-link.csv"
path_mat_mean_ts=pathOutputDir+prefix+"_mat_mean-ts.csv"
path_mat_mean_link=pathOutputDir+prefix+"_mat_mean-link.csv"

path_mat_selected=pathOutputDir+prefix+"_mat_selected.csv"
path_mat_selected_sum=pathOutputDir+prefix+"_mat_selected_sum.csv"
path_mat_selected_mean=pathOutputDir+prefix+"_mat_selected_mean.csv"

# logger and handleFiles
# ----------------------------------------------------------------------------------------------------------------------
hf=handleFiles.HandleFiles(logger=None)
hf.createDirectories(["outputs",pathOutputDir,pathOutputFig])
logger=logger.Logger(storeLog=True,initStore=True,pathLog=pathOutputDir+prefix+"_log_df-mat.md")
hf.setLogger(logger=logger)
logger.setDisplay(True,True,True,True)
logger.storeLocal(False)
cwd=hf.getDefCwd()
logger.log(cl=None,method=None,message="start create df for MATSim")

run_df_tra,run_df_cop,run_df_hbf_level,run_df_hbf_emissions,run_mergeDf,run_sumMean,selectScenarios=False,False,False,True,True,True,True

# create df base
logger.log(cl=None,method=None,message="start create df base")
# ----------------------------------------------------------------------------------------------------------------------
if run_df_tra:
    df_mat=pd.read_csv(filepath_or_buffer=path_mat_traffic,sep=",")

    logger.log(cl=None,method=None,message="handle name columns")
    df_mat=df_mat.rename(columns={'time':"ts", 'link_id':"id_link", 'lv_spd_d':'av_sp_kph', 'lv_d':"nVeh"})
    # df_mat=df_mat.fillna(0)
    df_mat["test"]=0
    df_mat.loc[df_mat["id_link"].str.contains("pt_",na=False),"test"]=1
    df_mat=df_mat[df_mat["test"]==0]
    # df_mat=df_mat.dropna()

    # df_mat.loc[df_mat["av_sp_kph"] >=123, "av_sp_kph"] = 123
    logger.log(cl=None,method=None,message="compute spatial speed")
    df_mat["av_sp_kph_round"]=np.floor(df_mat["av_sp_kph"]).astype("int")
    df_mat["av_sp_mps_round"]=np.floor(df_mat["av_sp_kph"]/3.6).astype("int")
    df_mat["av_sp_mps"]=np.floor(df_mat["av_sp_kph"]/3.6)

    logger.log(cl=None,method=None,message="add TD")
    df_mat["td"]=df_mat["length"]*df_mat["nVeh"]
    df_mat=df_mat[tools.dropValColumns(columns=list(df_mat.columns),listValToDrop=['pk','mv_d', 'mv_spd_d',    'pm10', 'fc', 'co', 'fc_mj', 'hc', 'nox', 'co2_rep', 'test' ])]

    df_mat=df_mat.drop_duplicates()

    print (df_mat)
    print (df_mat.describe())

    tools.storeDataframe(logger=logger,pathStore=path_mat_tra,df=df_mat)
# add emission copert
# ----------------------------------------------------------------------------------------------------------------------
if run_df_cop:
    logger.log(cl=None,method=None,message="compute copert")
    list_fe=["co2_g/km" , "nox_g/km",  "pm10_g/km"]
    list_tot_emi=["co2_g" , "nox_g",  "pm10_g"]
    df_mat=pd.read_csv(filepath_or_buffer=path_mat_tra,sep=";")
    df_cop=pd.read_csv(filepath_or_buffer=path_copert,sep=";")
    df_emi=pd.merge(df_mat,df_cop,left_on="av_sp_kph",right_on="speedInKph",how="left")
    for i in range(len(list_fe)):   df_emi[list_tot_emi[i]+"_cop"]=df_emi[list_fe[i]].astype("float")*df_emi["length"].astype("float")/1000*df_emi["nVeh"]                       # compute total emissions
    df_emi=df_emi[tools.dropValColumns(columns=list(df_emi.columns),listValToDrop=['speedInKph','Unnamed: 0_x','Unnamed: 0_y'])]
    df_emi=df_emi.rename(columns={'co2_g/km':"co2_g/km_cop", "nox_g/km":"nox_g/km_cop", "pm10_g/km":"pm10_g/km_cop"})
    print (df_emi)
    tools.storeDataframe(logger=logger,pathStore=path_mat_cop,df=df_emi)

if run_df_hbf_level:
    logger.log(cl=None,method=None,message="compute level HBEFA")
    df_mat=pd.read_csv(filepath_or_buffer=path_mat_tra,sep=";")
    df_hbf_lev=pd.read_csv(filepath_or_buffer=path_hbf_level,sep=";")
    df_hbf_trad=pd.read_csv(filepath_or_buffer=path_hbf_trad,sep=";")
    df_hbf_trad["triplet_en"]=df_hbf_trad["TS"].str.split("/",expand=True)[0]+"/"+df_hbf_trad["TS"].str.split("/",expand=True)[1]+"/"+df_hbf_trad["TS"].str.split("/",expand=True)[2]
    df_hbf_trad["triplet_fr"]=df_hbf_trad["TS_fr"].str.split("/",expand=True)[0]+"/"+df_hbf_trad["TS_fr"].str.split("/",expand=True)[1]+"/"+df_hbf_trad["TS_fr"].str.split("/",expand=True)[2]

    df_hbf_trad=df_hbf_trad[["triplet_en","triplet_fr"]].drop_duplicates()

    # add triplet to links
    df_mat=pd.merge(df_mat,df_hbf_trad,left_on="type",right_on="triplet_en",how="inner")
    df_mat["triplet_fr"] = df_mat["triplet_fr"].replace('Autor-Nat.','Autor-Urb', regex=True)

    # compute traffic level
    df_mat_level=None

    level=['/Fluide','/Dense','/Saturé','/Congestion','/Congestion2']
    ss=[]
    er=0
    for i in range(len(df_mat)):
        try:
            if df_mat.av_sp_kph[i] < float(df_hbf_lev.V[df_hbf_lev.TrafficSit==df_mat.triplet_fr[i]+level[4]]):         ss.append(df_mat.triplet_fr[i]+level[4])
            elif df_mat.av_sp_kph[i] < float(df_hbf_lev[df_hbf_lev.TrafficSit==df_mat.triplet_fr[i]+level[3]].V):       ss.append(df_mat.triplet_fr[i]+level[3])
            elif df_mat.av_sp_kph[i] < float(df_hbf_lev[df_hbf_lev.TrafficSit==df_mat.triplet_fr[i]+level[2]].V):       ss.append(df_mat.triplet_fr[i]+level[2])
            elif df_mat.av_sp_kph[i] < float(df_hbf_lev[df_hbf_lev.TrafficSit==df_mat.triplet_fr[i]+level[1]].V):       ss.append(df_mat.triplet_fr[i]+level[1])
            else:                                                                                                       ss.append(df_mat.triplet_fr[i]+level[0])
        except TypeError:
            logger.warning(cl=None,method=None,message="error n. {}".format(er),doQuit=False)
            er+=1
    df_mat_level = df_mat.assign(TrafficSit = ss)
    print (df_mat_level)
    tools.storeDataframe(logger=logger,pathStore=path_mat_level,df=df_mat_level)

if run_df_hbf_emissions:
    logger.log(cl=None,method=None,message="compute emissions HBEFA")
    df_links_level_fe=pd.read_csv(filepath_or_buffer=path_mat_level,sep=";")
    df_hbefa_ef=pd.read_csv(filepath_or_buffer=path_hbf_emission_factor,sep=";")

    # merge df
    df_links_poll=pd.merge(df_links_level_fe,df_hbefa_ef,left_on="TrafficSit",right_on="TrafficSit")

    # compute values for links
    df_links_poll["poll"]=df_links_poll["EFA_weighted"]*df_links_poll["td"] /1000   #  ??????????????????
    components=["NOx","PM (non-exhaust)", "CO2(rep)"]
    c_norm=["nox_g/km_hbf","co2_g/km_hbf","pm10_g/km_hbf"]
    df1=pd.DataFrame()

    for c in components:
        # print (c)
        # print (df_links_poll[df_links_poll["Component"]==c])
        df1=df1._append(df_links_poll[df_links_poll["Component"]==c])
    print (df1)
    for c in range (len(components)):
        df1.loc[df1["Component"]==components[c],components[c]]=df1["poll"]
        df1.loc[df1["Component"]==components[c],c_norm[c]]=df1["EFA_weighted"]
    df1=df1.fillna(0)
    print (df1)
    df1=df1.groupby(by=["id_link","ts"]).sum().reset_index()
    df1=df1[tools.dropValColumns(columns=list(df1.columns),listValToDrop=['type','Unnamed: 0.1','Unnamed: 0',
                                                                          'triplet_en','triplet_fr','TrafficSit','Component','EFA_weighted','poll'])]

    print (df1)
    tools.storeDataframe(logger=logger,pathStore=path_mat_hbf,df=df1)

    # components=df_links_poll["Component"].unique()
    # components=["NOx","PM (non-exhaust)", "CO2(rep)"]
    #
    # p=df_links_poll["ts"].unique()
    # df_final=pd.DataFrame()
    # df_final["id_link"]=df_links_poll["id_link"]
    # df_final["ts"]=df_links_poll["ts"]
    # df_final["td"]=df_links_poll["td"]
    # df_final["length"]=df_links_poll["length"]
    # df_final['nVeh']=df_links_poll['nVeh']
    # df_final['av_sp_mps']=df_links_poll['av_sp_mps']
    # # df_final=df_final.drop_duplicates(subset=["id_link","ts"])
    # df_final=df_final.drop_duplicates()
    #
    # for component in components:
    #     logger.log(cl=None,method=None,message="compute emissions for pollutant: {}".format(component))
    #     df1=df_links_poll[df_links_poll["Component"]==component]
    #     df1=df1[["poll","ts","id_link"]]
    #     df1.rename(columns = {'poll':component}, inplace = True)
    #     df_final=pd.merge(df_final,df1,left_on=["id_link","ts"],right_on=["id_link","ts"],how="inner")
    #
    # # df_final=df_final.drop_duplicates()
    # # df_final=df_final.drop_duplicates(subset=["id_link","ts"])
    #
    # print (df_final)
    # tools.storeDataframe(logger=logger,pathStore=path_mat_hbf,df=df_final)

if run_mergeDf:
    logger.log(cl=None,method=None,message="merge df")
    df_cop=pd.read_csv(filepath_or_buffer=path_mat_cop,sep=";")
    df_hbf=pd.read_csv(filepath_or_buffer=path_mat_hbf,sep=";")
    df_mat=pd.read_csv(filepath_or_buffer=path_mat_traffic,sep=",")
    df_1=pd.merge (df_cop,df_hbf,on=["id_link","ts"],how="left",suffixes=("","_hbf"))
    df_1=df_1.rename(columns={"NOx":"nox_g_hbf","PM (non-exhaust)":"pm10_g_hbf", "CO2(rep)":"co2_g_hbf" })
    # df_1=df_1[tools.dropValColumns(columns=list(df_1.columns),listValToDrop=['Unnamed: 0', 'Unnamed: 0_hbf', 'td_hbf', 'length_hbf', 'nVeh_hbf', 'av_sp_mps_hbf',  'HC', 'CO',  'mcarb', 'carb_MJ', 'PM',  'CO2(total)', 'PM2.5',"PM2.5 (non-exhaust)"  ])]
    df_1=df_1[tools.dropValColumns(columns=list(df_1.columns),listValToDrop=['Unnamed: 0', 'Unnamed: 0_hbf', 'td_hbf', 'length_hbf', 'nVeh_hbf', 'av_sp_mps_hbf',     ])]

    df_1=df_1.fillna(0)
    print (df_1)
    tools.storeDataframe(logger=logger,pathStore=path_mat_emi,df=df_1)

if run_sumMean:
    logger.log(cl=None,method=None,message="sum and mean df")
    df_mat=pd.read_csv(filepath_or_buffer=path_mat_emi,sep=";")
    logger.log(cl=None,method=None,message="sum by ts")
    df_1=df_mat[tools.dropValColumns(columns=list(df_mat.columns),listValToDrop=['Unnamed: 0', 'type',"id_link"])]
    df_1=df_1.groupby(by="ts").sum().reset_index()
    print (df_1)
    tools.storeDataframe(logger=logger,pathStore=path_mat_sum_ts,df=df_1)

    logger.log(cl=None,method=None,message="sum by links")
    df_1=df_mat[tools.dropValColumns(columns=list(df_mat.columns),listValToDrop=['Unnamed: 0', 'type',"ts"])]
    df_1=df_1.groupby(by="id_link").sum().reset_index()
    print (df_1)
    tools.storeDataframe(logger=logger,pathStore=path_mat_sum_link,df=df_1)

    logger.log(cl=None,method=None,message="mean by ts")
    df_1=df_mat[tools.dropValColumns(columns=list(df_mat.columns),listValToDrop=['Unnamed: 0', 'type',"id_link"])]
    df_1=df_1.groupby(by="ts").mean().reset_index()
    print (df_1)
    tools.storeDataframe(logger=logger,pathStore=path_mat_mean_ts,df=df_1)

    logger.log(cl=None,method=None,message="mean by links")
    df_1=df_mat[tools.dropValColumns(columns=list(df_mat.columns),listValToDrop=['Unnamed: 0', 'type',"ts"])]
    df_1=df_1.groupby(by="id_link").mean().reset_index()
    print (df_1)
    tools.storeDataframe(logger=logger,pathStore=path_mat_mean_link,df=df_1)

if selectScenarios:
    logger.log(cl=None,method=None,message="get df with selected ts")
    scenarios=["6:00","8:00","9:30","15:00","17:30","22:00"]
    scenarios_sec=[tools.get_second(_) for _ in scenarios]
    df_mat=pd.read_csv(filepath_or_buffer=path_mat_emi,sep=";")

    logger.log(cl=None,method=None,message="select ts: "+str(scenarios))
    df1=pd.DataFrame()
    for ts in scenarios_sec:        df1=df1._append(df_mat[df_mat["ts"]==ts])
    df1=df1[tools.dropValColumns(columns=list(df1.columns),listValToDrop=['Unnamed: 0'])]

    print (df1)
    tools.storeDataframe(logger=logger,pathStore=path_mat_selected,df=df1)

    df1=df1[tools.dropValColumns(columns=list(df1.columns),listValToDrop=[ 'type',"id_link"])]

    logger.log(cl=None,method=None,message="sum selected scenarios")
    df2=df1.groupby(by="ts").sum().reset_index()
    print (df2)
    tools.storeDataframe(logger=logger,pathStore=path_mat_selected_sum,df=df2)

    logger.log(cl=None,method=None,message="mean selected scenarios")
    df2=df1.groupby(by="ts").mean().reset_index()
    print (df2)
    tools.storeDataframe(logger=logger,pathStore=path_mat_selected_mean,df=df2)
