# Modified from the original file, which can be found in https://github.com/USArmyResearchLab/ParaPower
# Github Repo: https://github.com/FhG-IISB/ParaPowerPython
# Developed by: Fraunhofer IISB

from PPTCM import PPTCM

def ConvertToPPTCM(data):
    pout = PPTCM()
    fFields = list(pout.features().keys())
    Fields = list(data.keys())
    
    for ThisField in Fields:
        if ThisField == "ExternalConditions":
            pout.ExternalConditions["h_Xminus"] = data["ExternalConditions"]["h_Left"]
            pout.ExternalConditions["h_Xplus"] = data["ExternalConditions"]["h_Right"]
            pout.ExternalConditions["h_Yplus"] = data["ExternalConditions"]["h_Front"]
            pout.ExternalConditions["h_Yminus"] = data["ExternalConditions"]["h_Back"]
            pout.ExternalConditions["h_Zplus"] = data["ExternalConditions"]["h_Top"]
            pout.ExternalConditions["h_Zminus"] = data["ExternalConditions"]["h_Bottom"]

            pout.ExternalConditions["Ta_Xminus"] = data["ExternalConditions"]["Ta_Left"]
            pout.ExternalConditions["Ta_Xplus"] = data["ExternalConditions"]["Ta_Right"]
            pout.ExternalConditions["Ta_Yplus"] = data["ExternalConditions"]["Ta_Front"]
            pout.ExternalConditions["Ta_Yminus"] = data["ExternalConditions"]["Ta_Back"]
            pout.ExternalConditions["Ta_Zplus"] = data["ExternalConditions"]["Ta_Top"]
            pout.ExternalConditions["Ta_Zminus"] = data["ExternalConditions"]["Ta_Bottom"]

            pout.ExternalConditions["Tproc"] = data["ExternalConditions"]["Tproc"]
        elif ThisField == "Params":
            pout.iParams = data["Params"]
            pout.Params = data["Params"]
        elif ThisField == "Features":
            for i in range(len(data["Features"])):
                features = {}
                ThisFeature = data["Features"][i]
                for key in fFields:
                    if key == "Desc":
                        old_key = "name"
                    else:
                        old_key = key
                    features[key] = ThisFeature[old_key]
                pout.Features.append(features)
        elif ThisField == "PottingMaterial":
            pout.PottingMaterial = data["PottingMaterial"]
        elif ThisField == "MatLib":
            pout.MatLib = data["MatLib"]
        elif ThisField == "Version":
            pout.Version = data["Version"]
        else:
            raise ValueError("Field not recognized!")
        
    return pout
                    

