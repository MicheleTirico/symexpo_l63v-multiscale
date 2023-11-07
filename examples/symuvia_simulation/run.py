from symupy.runtime.api import Simulator, Simulation
from toolbox.control import logger
from toolbox.control import handleFiles
import os

# paths and parametetes
prefix= "l63v-base"#                                "Lafayette"#"5x5grid"
nameXml="L63V_symuflow_input.xml"#"Lafayette-02"+".xml"#5x5grid.xml"

scenario=prefix
pathOutputDir="outputs/"+scenario+"/"
pathResources="resources/"+scenario+"/"
path_xml=os.path.abspath(pathResources+nameXml)
path_output_out=pathResources+"OUT/"
path_output_sim=pathOutputDir+"sim/"

# logger and handleFiles
# ----------------------------------------------------------------------------------------------------------------------
hf=handleFiles.HandleFiles(logger=None)
hf.createDirectories(["outputs",pathOutputDir,path_output_sim])
logger=logger.Logger(storeLog=True,initStore=True,pathLog=pathOutputDir+prefix+"_log_run_symupy.md")
hf.setLogger(logger=logger)
logger.setDisplay(True,True,True,True)
logger.storeLocal(False)
cwd=hf.getDefCwd()
logger.log(cl=None,method=None,message="start run symupy")

# run simulation
# ----------------------------------------------------------------------------------------------------------------------
logger.log(cl=None,method=None,message="initialize simulation")
s=Simulator()
s.register_simulation(path_xml)
logger.log(cl=None,method=None,message="start simutaion")
s.run()
logger.log(cl=None,method=None,message="end simutaion")

# handle files
# ----------------------------------------------------------------------------------------------------------------------
# logger.log(cl=None,method=None,message="move outputs from to {}".format(path_output_sim)
# shutil.move(path_output_out,pathOutputDir)
hf.copyFilesFromDirectory(path_output_out,path_output_sim)
