import pandas as pd
import numpy as np
from toolbox.control import logger
from toolbox.control import handleFiles
from toolbox.control import tools

# paths and parametetes
prefix="l63v-multiscale"
scenario=prefix+"_"+"03"
pathOutputDir="outputs/"+scenario+"/"
pathOutputDir_od=pathOutputDir+"od/"
pathResources="resources/"
pathResources_od=pathResources+"od_matrix_01/"

path_points_merged=pathResources_od+"symexpo_l63v_mat_point_all_merged.csv"
path_points_merged_filtered=pathOutputDir_od+"symexpo_l63v_mat_point_all_merged_filtered.csv"

# logger and handleFiles
# ----------------------------------------------------------------------------------------------------------------------
hf=handleFiles.HandleFiles(logger=None)
hf.createDirectories([pathOutputDir,pathOutputDir_od])
logger=logger.Logger(storeLog=True,initStore=True,pathLog=pathOutputDir_od+prefix+"_log_od_get_ports.md")
hf.setLogger(logger=logger)
logger.setDisplay(True,True,True,True)
logger.storeLocal(False)
cwd=hf.getDefCwd()
logger.log(cl=None,method=None,message="start to create df for ports symuvia")

# read df
# ----------------------------------------------------------------------------------------------------------------------
df_points_merged=pd.read_csv(path_points_merged,sep=";")
print (df_points_merged)

# get filters
df_points_merged.loc[df_points_merged["layer"].str.contains("end"), 'is_end'] = 1
df_points_merged.loc[df_points_merged["layer"].str.contains("start"), 'is_start'] = 1
df_points_merged.loc[df_points_merged["layer"].str.contains("outside"), 'is_outside'] = 1
df_points_merged.loc[df_points_merged["layer"].str.contains("inside"), 'is_inside'] = 1
df_points_merged=df_points_merged.fillna(0)
df_points_merged=df_points_merged[tools.dropValColumns(columns=list(df_points_merged.columns),listValToDrop=['person', 'trip_numbe',  'trav_time','wait_time', 'traveled_d', 'euclidean_', 'main_mode', 'longest_di', 'start_acti', 'end_activi', 'start_faci','end_facili','first_pt_b', 'last_pt_eg', 'layer', 'path'])]

# select only car mode
df_points_merged=df_points_merged[df_points_merged["modes"]=="car"]

print (df_points_merged)
tools.storeDataframe(logger=logger,pathStore=path_points_merged_filtered,df=df_points_merged)

