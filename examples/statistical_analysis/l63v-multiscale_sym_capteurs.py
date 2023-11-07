from lxml import etree
import pandas as pd
from toolbox.control import logger
from toolbox.control import handleFiles
import csv

def computeSelectedColums(tree,pathStore):
    logger.log(cl=None,method=None,message="start  compute compute list of selected values")
    p,id,distance_totale_parcourue,vitesse_spatiale,debit_sortie ,temps_total_passe= [],[],[],[],[],[]
    for periode in tree.xpath("/OUT/SIMULATION/GESTION_CAPTEUR/CAPTEURS_MFD/PERIODE"):
        logger.log(cl=None,method=None,message="read the period: {}".format(periode))
        for capt in periode.xpath("CAPTEURS/CAPTEUR"):
            p.append(float(periode.get("debut")))
            id.append(str(capt.get("id")))
            distance_totale_parcourue.append(float(capt.get("distance_totale_parcourue")))
            vitesse_spatiale.append(float(capt.get("vitesse_spatiale")))
            debit_sortie.append(float(capt.get("debit_sortie")))
            temps_total_passe.append(float(capt.get("temps_total_passe")))
            if capt.get("id")=="CAPT_T_997243908_toRef":break

    df2 = pd.DataFrame({"p" : p,"id": id,"distance_totale_parcourue": distance_totale_parcourue,"vitesse_spatiale": vitesse_spatiale,"debit_sortie":debit_sortie,"temps_total_passe":temps_total_passe})

    logger.log(cl=None,method=None,message="start store dataframe in:{}".format(pathStore))
    df2.to_csv(pathStore, sep=';')
    logger.log(cl=None,method=None,message="finish compute compute list of selected values")
def computeAllColumns(tree,pathStore):
    logger.log(cl=None,method=None,message="start  compute compute list of all values")
    test=False
    with open(pathStore, 'w') as f:
        writer=csv.writer(f,delimiter=";")
        for periode in tree.xpath("/OUT/SIMULATION/GESTION_CAPTEUR/CAPTEURS_MFD/PERIODE"):
            logger.log(cl=None,method=None,message="read the period: {}".format(periode))
            p=periode.get("debut")
            if test==False:# and periode.xpath("CAPTEURS/CAPTEUR")[0].attrib["id"]!="sensor_network" :

                header=["p"]+[i for i in periode.xpath("CAPTEURS/CAPTEUR")[0].attrib]
                writer.writerow(header)
                test=True
            for capt in periode.xpath("CAPTEURS/CAPTEUR"):
                # id=capt.get("id")
                # print (id,id[0:6])
                if capt.get("id")[0:6] == "CAPT_T":
                    # print (capt)
                    line =[p]
                    for attrib in capt.attrib:    line.append(capt.get(attrib))
                    writer.writerow(line)
                    # if capt.get("id")=="CAPT_T_997243908_toRef":break

    logger.log(cl=None,method=None,message="csv stored in:{}".format(pathStore))
    logger.log(cl=None,method=None,message="finish compute list of all values")
def computeCapteursGlobal(tree,pathStore):
    logger.log(cl=None,method=None,message="start  compute compute capteurs global")
    with open(pathStore, 'w') as f:
        writer=csv.writer(f,delimiter=";")
        header=[i for i in tree.xpath("/OUT/SIMULATION/GESTION_CAPTEUR/CAPTEUR_GLOBAL/PERIODE")[0].attrib]
        writer.writerow(header)

        for periode in tree.xpath("/OUT/SIMULATION/GESTION_CAPTEUR/CAPTEUR_GLOBAL/PERIODE"):
            logger.log(cl=None,method=None,message="read the period: {}".format(periode))
            line =[]

            for attrib in periode.attrib:    line.append(periode.get(attrib))

            writer.writerow(line)

    logger.log(cl=None,method=None,message="csv stored in:{}".format(pathStore))
    logger.log(cl=None,method=None,message="finish compute capteurs global ")
def computeTrajectoires(tree,pathStore):
    logger.log(cl=None,method=None,message="start  compute compute trajectoires")
    with open(pathStore, 'w') as f:
        writer=csv.writer(f,delimiter=";")
        # header=[i for i in tree.xpath("/OUT/SIMULATION/VEHS/VEH")[0].attrib]
        header=["id","dstParcourue","entree","instC","instE","instS","itineraire","sortie","lib","type","vx","w"]

        writer.writerow(header)
        for veh in tree.xpath("/OUT/SIMULATION/VEHS/VEH"):
            logger.log(cl=None,method=None,message="read the vehicle: {}".format(veh.attrib["id"]))

            line =[]

            for attrib in header:        line.append(veh.get(attrib))
            # for attrib in veh.attrib:    line.append(veh.get(attrib))

            writer.writerow(line)

    logger.log(cl=None,method=None,message="csv stored in:{}".format(pathStore))
    logger.log(cl=None,method=None,message="finish compute trajectoires ")

# ----------------------------------------------------------------------------------------------------------------------

# paths and parametetes
prefix="l63v-multiscale"
scenario=prefix+"_"+"03"
pathOutputDir="outputs/"+scenario+"/"
pathResources="resources/"
pathOutputFig=pathOutputDir+"fig/"

# files to set
fileName = 'l63v-multiscale_000000_235959_traf'
pathFileTraffic=pathOutputDir+"sim_se/"+fileName+".xml"

# logger and handleFiles
# ----------------------------------------------------------------------------------------------------------------------
hf=handleFiles.HandleFiles(logger=None)
hf.createDirectories([pathOutputDir,pathOutputFig])
logger=logger.Logger(storeLog=True,initStore=True,pathLog="outputs/"+scenario+"/"+prefix+"_log_parseCapteurs.md")
hf.setLogger(logger=logger)
logger.setDisplay(True,True,True,True)
logger.storeLocal(False)
cwd=hf.getDefCwd()
logger.log(cl=None,method=None,message="start  compute parse Symuvia capteurs")
run_capteurs_all,run_capteurs_selected,run_capteurs_global,run_trajectoires=True,True,True,True

# parse capteurs
# ----------------------------------------------------------------------------------------------------------------------

logger.log(cl=None,method=None,message="start  read tree")
tree = etree.parse(pathFileTraffic)
logger.log(cl=None,method=None,message="finish read tree")
if run_capteurs_all:                    computeAllColumns(tree,pathOutputDir+prefix+"_sym_capteurs_all.csv")
if run_capteurs_selected:               computeSelectedColums(tree,pathOutputDir+fileName +"_capteurs.csv")
if run_capteurs_global:                 computeCapteursGlobal(tree,pathOutputDir+fileName +"_capteurs_global.csv")
if run_trajectoires:                    computeTrajectoires(tree, pathOutputDir+fileName +"_trajectoires.csv")
logger.log(cl=None,method=None,message="finish compute parse Symuvia capteurs")
