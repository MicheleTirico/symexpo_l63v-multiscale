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
path_sym_traffic=pathOutputDir+prefix+"_000000_235959_traf_capteurs.csv"
path_copert=pathOutputDir+prefix+"_copert"+".csv"
path_sym_links_len=pathResources+"links027_len.csv"
path_sym_tra=pathOutputDir+prefix+"_sym_df-tra.csv"
path_sym_cop=pathOutputDir+prefix+"_sym_df-tra-cop.csv"

path_hbf=pathOutputDir+prefix+"_hbfea.csv"
path_links=pathOutputDir+prefix+"_sym_links.csv"
path_hbf_level=pathResources+"TS_HBEFA_TAP23.csv"
path_sym_level=pathOutputDir+prefix+"_sym_hbf_level.csv"
path_hbf_fe=pathOutputDir+prefix+"_hbfea.csv"
path_sym_hbf=pathOutputDir+prefix+"_sym_df-hbf.csv"
path_sym_emi=pathOutputDir+prefix+"_sym_tra-emi.csv"

path_sym_sum_ts=pathOutputDir+prefix+"_sym_sum-ts.csv"
path_sym_sum_link=pathOutputDir+prefix+"_sym_sum-link.csv"
path_sym_mean_ts=pathOutputDir+prefix+"_sym_mean-ts.csv"
path_sym_mean_link=pathOutputDir+prefix+"_sym_mean-link.csv"

path_sym_selected=pathOutputDir+prefix+"_sym_selected.csv"
path_sym_selected_sum=pathOutputDir+prefix+"_sym_selected_sum.csv"
path_sym_selected_mean=pathOutputDir+prefix+"_sym_selected_mean.csv"

# logger and handleFiles
# ----------------------------------------------------------------------------------------------------------------------
hf=handleFiles.HandleFiles(logger=None)
hf.createDirectories(["outputs",pathOutputDir,pathOutputFig])
logger=logger.Logger(storeLog=True,initStore=True,pathLog=pathOutputDir+prefix+"_log_df-sym.md")
hf.setLogger(logger=logger)
logger.setDisplay(True,True,True,True)
logger.storeLocal(False)
cwd=hf.getDefCwd()
logger.log(cl=None,method=None,message="start create df for symuvia")

run_df_tra,run_df_cop,run_df_hbf_level,run_df_hbf_emissions,run_mergeDf,run_sumMean,selectScenarios=False,False,False,True,True,True,True
# create df base
logger.log(cl=None,method=None,message="start create df base")
# ----------------------------------------------------------------------------------------------------------------------
if run_df_tra:
    df_sym=pd.read_csv(filepath_or_buffer=path_sym_traffic,sep=";")
    logger.log(cl=None,method=None,message="handle name columns")
    df_sym=df_sym.rename(columns={'p':"ts", 'id':"id_capt", 'distance_totale_parcourue':"td", 'vitesse_spatiale':'av_sp_mps', 'debit_sortie':"nVeh", 'temps_total_passe':"tt"})
    df_sym["id_link"]=df_sym["id_capt"].str.replace("CAPT_","")                  # get id links

    logger.log(cl=None,method=None,message="compute spatial speed")
    df_sym["av_sp_mps_round"]=np.floor(df_sym["av_sp_mps"]).astype("int")
    df_sym["av_sp_kph_round"]=np.floor(df_sym["av_sp_mps"]*3.6).astype("int")
    df_sym["av_sp_kph"]=np.floor(df_sym["av_sp_mps"]*3.6)

    logger.log(cl=None,method=None,message="add length")
    df_sym_len=pd.read_csv(filepath_or_buffer=path_sym_links_len,sep=",")
    df_sym=pd.merge(df_sym,df_sym_len,right_on="ID",left_on="id_link")
    df_sym=df_sym[tools.dropValColumns(columns=list(df_sym.columns),listValToDrop=["Unnamed: 0","Zone_I","ID","Indice"])]
    df_sym=df_sym.drop_duplicates()
    print (df_sym)
    print (df_sym.describe())
    tools.storeDataframe(logger=logger,pathStore=path_sym_tra,df=df_sym)

# add emission copert
# ----------------------------------------------------------------------------------------------------------------------
if run_df_cop:
    logger.log(cl=None,method=None,message="compute copert")
    list_fe=["co2_g/km" , "nox_g/km",  "pm10_g/km"]
    list_tot_emi=["co2_g" , "nox_g",  "pm10_g"]
    df_sym=pd.read_csv(filepath_or_buffer=path_sym_tra,sep=";")
    df_cop=pd.read_csv(filepath_or_buffer=path_copert,sep=";")
    df_emi=pd.merge(df_sym,df_cop,left_on="av_sp_kph_round",right_on="speedInKph",how="left")
    for i in range(len(list_fe)):   df_emi[list_tot_emi[i]+"_cop"]=df_emi[list_fe[i]].astype("float")*df_emi["length"].astype("float")/1000*df_emi["nVeh"]                       # compute total emissions
    df_emi=df_emi[tools.dropValColumns(columns=list(df_emi.columns),listValToDrop=['speedInKph','Unnamed: 0_x','Unnamed: 0_y'])]
    df_emi=df_emi.rename(columns={'co2_g/km':"co2_g/km_cop", "nox_g/km":"nox_g/km_cop", "pm10_g/km":"pm10_g/km_cop"})
    df_emi=df_emi.fillna(0)
    print (df_emi)
    print (df_emi.describe())

    tools.storeDataframe(logger=logger,pathStore=path_sym_cop,df=df_emi)

if run_df_hbf_level:
    logger.log(cl=None,method=None,message="compute level HBEFA")
    df_sym=pd.read_csv(filepath_or_buffer=path_sym_tra,sep=";")
    df_links=pd.read_csv(filepath_or_buffer=path_links,sep=";")
    df_hbf_lev=pd.read_csv(filepath_or_buffer=path_hbf_level,sep=";")

    logger.log(cl=None,method=None,message="set limit speed")
    df_1=pd.merge(df_sym,df_links[["id","aut_speed_mps"]],left_on="id_link",right_on="id")
    print (df_1)
    df_1=df_1.fillna(50/3.6)
    df_1["aut_speed_kpm"]=np.round(df_1["aut_speed_mps"]*3.6).astype("int")
    df_sym=df_1[tools.dropValColumns(columns=list(df_1.columns),listValToDrop=['id',"aut_speed_mps"])]
    print (df_sym)

    logger.log(cl=None,method=None,message="set triplet")
    # df_sym.loc[df_sym["aut_speed_kpm"]==90,"triplet_en"]="URB/MW-City/90"
    # df_sym.loc[df_sym["aut_speed_kpm"]==72,"triplet_en"]="URB/MW-City/80"
    # df_sym.loc[df_sym["aut_speed_kpm"]==70,"triplet_en"]="URB/Distr/70"
    # df_sym.loc[df_sym["aut_speed_kpm"]==50,"triplet_en"]="URB/Distr/50"
    # df_sym.loc[df_sym["aut_speed_kpm"]<=30,"triplet_en"]="URB/Distr/30"

    df_sym.loc[df_sym["aut_speed_kpm"]==90,"triplet_fr"]="URB/Autor-Urb/90"
    df_sym.loc[df_sym["aut_speed_kpm"]==72,"triplet_fr"]="URB/Autor-Urb/80"
    df_sym.loc[df_sym["aut_speed_kpm"]==70,"triplet_fr"]="URB/Distrib/70"
    df_sym.loc[df_sym["aut_speed_kpm"]==50,"triplet_fr"]="URB/Distrib/50"
    df_sym.loc[df_sym["aut_speed_kpm"]<=30,"triplet_fr"]="URB/Distrib/30"

    level=['/Fluide','/Dense','/Saturé','/Congestion','/Congestion2']
    ss=[]

    logger.log(cl=None,method=None,message="start compute level")
    er=0
    for i in range(len(df_sym)):
        # print (i)
        try:
            if df_sym.av_sp_kph[i] < float(df_hbf_lev.V[df_hbf_lev.TrafficSit==df_sym.triplet_fr[i]+level[4]]):         ss.append(df_sym.triplet_fr[i]+level[4])
            elif df_sym.av_sp_kph[i] < float(df_hbf_lev[df_hbf_lev.TrafficSit==df_sym.triplet_fr[i]+level[3]].V):       ss.append(df_sym.triplet_fr[i]+level[3])
            elif df_sym.av_sp_kph[i] < float(df_hbf_lev[df_hbf_lev.TrafficSit==df_sym.triplet_fr[i]+level[2]].V):       ss.append(df_sym.triplet_fr[i]+level[2])
            elif df_sym.av_sp_kph[i] < float(df_hbf_lev[df_hbf_lev.TrafficSit==df_sym.triplet_fr[i]+level[1]].V):       ss.append(df_sym.triplet_fr[i]+level[1])
            else:                                                                                                       ss.append(df_sym.triplet_fr[i]+level[0])
        except TypeError:            logger.warning(cl=None,method=None,message="error n. {}".format(er),doQuit=False)

    df_sym_level = df_sym.assign(TrafficSit = ss)
    logger.log(cl=None,method=None,message="end  compute level")
    print (df_sym_level)
    tools.storeDataframe(logger=logger,pathStore=path_sym_level,df=df_sym_level)

if run_df_hbf_emissions:
    logger.log(cl=None,method=None,message="compute emissions HBEFA")
    df_hbf_fe=pd.read_csv(filepath_or_buffer=path_hbf_fe,sep=";")
    df_sym_level=pd.read_csv(filepath_or_buffer=path_sym_level,sep=";")

    print (df_hbf_fe)
    print (df_sym_level)
    df_sym_level=df_sym_level.rename(columns={"TrafficSit":'ts_fr'})

    #     merge df
    df_links_poll=pd.merge(df_sym_level,df_hbf_fe,left_on="ts_fr",right_on="ts_fr")

    # compute values for links
    df_links_poll["poll"]=df_links_poll["EFA_weighted"]*df_links_poll["td"]  /1000  #  ??????????????????
    components=["NOx","PM (non-exhaust)", "CO2(rep)"]
    c_norm=["nox_g/km_hbf","co2_g/km_hbf","pm10_g/km_hbf"]
    df1=pd.DataFrame()
    for c in components:
        df1=df1._append(df_links_poll[df_links_poll["Component"]==c])

    for c in range (len(components)):
        df1.loc[df1["Component"]==components[c],components[c]]=df1["poll"]
        df1.loc[df1["Component"]==components[c],c_norm[c]]=df1["EFA_weighted"]
    df1=df1.fillna(0)
    df1=df1.groupby(by=["id_link","ts"]).sum().reset_index()

    df1=df1[tools.dropValColumns(columns=list(df1.columns),listValToDrop=[ 'Unnamed: 0.1', 'Unnamed: 0_x', 'id_capt', 'aut_speed_kpm', 'triplet_fr', 'ts_fr',
                                                                           'Unnamed: 0_y', 'Component', 'IDTS', 'ts_en', 'poll'])]

    df1=df1.rename(columns={"NOx":"nox_g_hbf","CO2(rep)":"co2_g_hbf","PM (non-exhaust)":"pm10_g_hbf"})

    tools.storeDataframe(logger=logger,pathStore=path_sym_hbf,df=df1)

    # # compute values for links
    # df_links_poll["poll"]=df_links_poll["EFA_weighted"]*df_links_poll["td"] /1000 #  ??????????????????
    #
    # components=df_links_poll["Component"].unique()
    # p=df_links_poll["ts"].unique()
    #
    # print (df_links_poll)
    # df_final=pd.DataFrame()
    # df_final["id_link"]=df_links_poll["id_link"]
    # df_final["ts"]=df_links_poll["ts"]
    # df_final["td"]=df_links_poll["td"]
    # df_final["length"]=df_links_poll["length"]
    # df_final['nVeh']=df_links_poll['nVeh']
    # df_final['av_sp_mps']=df_links_poll['av_sp_mps']
    # df_final["ts_fr"]=df_links_poll['ts_fr']
    # print (df_links_poll.columns)
    # # df_final=df_final.drop_duplicates(subset=["id_link","ts"])
    #
    # for component in components:
    #     logger.log(cl=None,method=None,message="compute emissions for pollutant: {}".format(component))
    #     df1=df_links_poll[df_links_poll["Component"]==component]
    #     df1=df1[["poll","ts","id_link"]]
    #     df1.rename(columns = {'poll':component}, inplace = True)
    #     df_final=pd.merge(df_final,df1,left_on=["id_link","ts"],right_on=["id_link","ts"],how="inner")
    #
    # print (df_final.columns)
    # df_final=df_final[tools.dropValColumns(columns=list(df_final.columns),listValToDrop=['HC', 'CO',  'mcarb', 'carb_MJ', 'PM', 'CO2(total)', 'PM2.5', 'PM2.5 (non-exhaust)'])]
    # df_final=df_final.rename(columns={"NOx":"nox_g_hbf","CO2(rep)":"co2_g_hbf","PM (non-exhaust)":"pm10_g_hbf"})
    #
    # df_final=df_final.drop_duplicates()#(subset=["id_link","ts"])
    #
    # print (df_final)
    #
    # tools.storeDataframe(logger=logger,pathStore=path_sym_hbf,df=df_final)

if run_mergeDf:
    logger.log(cl=None,method=None,message="merge df")
    df_cop=pd.read_csv(filepath_or_buffer=path_sym_cop,sep=";")
    df_hbf=pd.read_csv(filepath_or_buffer=path_sym_hbf,sep=";")
    df_sym=pd.read_csv(filepath_or_buffer=path_sym_traffic,sep=";")
    df_1=pd.merge (df_cop,df_hbf,on=["id_link","ts"],how="left",suffixes=("","_hbf"))
    df_1=df_1[tools.dropValColumns(columns=list(df_1.columns),listValToDrop=['Unnamed: 0', 'Unnamed: 0_hbf', 'td_hbf', 'length_hbf', 'nVeh_hbf', 'av_sp_mps_hbf', 'id_capt','tt_hbf', 'av_sp_mps_round_hbf',
                                                                             'av_sp_kph_round_hbf', 'av_sp_kph_hbf',])]
    df_1=df_1.fillna(0)
    print (df_1)
    tools.storeDataframe(logger=logger,pathStore=path_sym_emi,df=df_1)

if run_sumMean:
    logger.log(cl=None,method=None,message="sum and mean df")
    df_sym=pd.read_csv(filepath_or_buffer=path_sym_emi,sep=";")
    print (df_sym.columns)

    logger.log(cl=None,method=None,message="sum by ts")

    df_1=df_sym[tools.dropValColumns(columns=list(df_sym.columns),listValToDrop=['Unnamed: 0',"id_link"])]
    df_1=df_1.groupby(by="ts").sum().reset_index()
    print (df_1)
    tools.storeDataframe(logger=logger,pathStore=path_sym_sum_ts,df=df_1)

    logger.log(cl=None,method=None,message="sum by links")
    df_1=df_sym[tools.dropValColumns(columns=list(df_sym.columns),listValToDrop=['Unnamed: 0',"ts"])]
    df_1=df_1.groupby(by="id_link").sum().reset_index()
    print (df_1)
    tools.storeDataframe(logger=logger,pathStore=path_sym_sum_link,df=df_1)

    logger.log(cl=None,method=None,message="mean by ts")
    df_1=df_sym[tools.dropValColumns(columns=list(df_sym.columns),listValToDrop=['Unnamed: 0',"id_link"])]
    df_1=df_1.groupby(by="ts").mean().reset_index()
    print (df_1)
    tools.storeDataframe(logger=logger,pathStore=path_sym_mean_ts,df=df_1)

    logger.log(cl=None,method=None,message="mean by links")
    df_1=df_sym[tools.dropValColumns(columns=list(df_sym.columns),listValToDrop=['Unnamed: 0',"ts"])]
    df_1=df_1.groupby(by="id_link").mean().reset_index()
    print (df_1)
    tools.storeDataframe(logger=logger,pathStore=path_sym_mean_link,df=df_1)

if selectScenarios:
    logger.log(cl=None,method=None,message="get df with selected ts")
    scenarios=["6:00","8:00","9:30","15:00","17:30","22:00"]
    scenarios_sec=[tools.get_second(_) for _ in scenarios]
    df_sym=pd.read_csv(filepath_or_buffer=path_sym_emi,sep=";")

    logger.log(cl=None,method=None,message="select ts: "+str(scenarios))
    df1=pd.DataFrame()
    for ts in scenarios_sec:        df1=df1._append(df_sym[df_sym["ts"]==ts])
    df1=df1[tools.dropValColumns(columns=list(df1.columns),listValToDrop=['Unnamed: 0'])]

    print (df1)
    tools.storeDataframe(logger=logger,pathStore=path_sym_selected,df=df1)

    df1=df1[tools.dropValColumns(columns=list(df1.columns),listValToDrop=[ "id_link"])]

    logger.log(cl=None,method=None,message="sum selected scenarios")
    df2=df1.groupby(by="ts").sum().reset_index()
    print (df2)
    tools.storeDataframe(logger=logger,pathStore=path_sym_selected_sum,df=df2)

    logger.log(cl=None,method=None,message="mean selected scenarios")
    df2=df1.groupby(by="ts").mean().reset_index()
    print (df2)
    tools.storeDataframe(logger=logger,pathStore=path_sym_selected_mean,df=df2)
