
from toolbox.control import logger
from toolbox.control import handleFiles
import csv
from lxml import etree

# paths and parametetes
prefix="l63v-multiscale"
scenario=prefix+"_"+"02"
pathOutputDir="outputs/"+scenario+"/"
pathResources="resources/"
pathOutputFig=pathOutputDir+"fig/"

# path
path_xml=pathOutputDir+"sim_es/"+"l63v-multiscale_000000_235959_traf.xml"
path_links=pathOutputDir+prefix+"_sym_links.csv"


# logger and handleFiles
# ----------------------------------------------------------------------------------------------------------------------
hf=handleFiles.HandleFiles(logger=None)
hf.createDirectories([pathOutputDir,pathOutputFig])
logger=logger.Logger(storeLog=True,initStore=True,pathLog="outputs/"+scenario+"/"+prefix+"_log_sym-links.md")
hf.setLogger(logger=logger)
logger.setDisplay(True,True,True,True)
logger.storeLocal(False)
cwd=hf.getDefCwd()

# ----------------------------------------------------------------------------------------------------------------------
logger.log(cl=None,method=None,message="start create links")
tree = etree.parse(path_xml)

with open(path_links, 'w') as f:
    writer=csv.writer(f,delimiter=";")
    for troncons in tree.xpath("/OUT/IN/RESEAU/TRONCONS"):#("/OUT/IN/RESEAUX/RESEAU/TRONCONS"):
        logger.log(cl=None,method=None,message="read troncon period: {}".format(troncons))
        # writer.writerow([i for i in troncons[0].attrib])
        header=["id","node_start","node_end","coord_start","coord_end","width","length","n_lines","aut_speed_mps"]
        writer.writerow(header)
        for t in troncons:
            logger.log(cl=None,method=None,message="read the period: {}".format(t))
            line =[]
            line.append(t.get("id"))
            line.append(t.get("id_eltamont"))
            line.append(t.get("id_eltaval"))
            line.append(t.get("extremite_amont"))
            line.append(t.get("extremite_aval"))
            line.append(t.get("largeur_voie"))
            line.append(t.get("longueur"))
            line.append(t.get("nb_voie"))
            line.append(t.get("vit_reg"))
            writer.writerow(line)

    logger.log(cl=None,method=None,message="csv stored in:{}".format(path_links))
    logger.log(cl=None,method=None,message="finish compute links")