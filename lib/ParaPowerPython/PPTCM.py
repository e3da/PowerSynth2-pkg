# Modified from the original file, which can be found in https://github.com/USArmyResearchLab/ParaPower
# Github Repo: https://github.com/FhG-IISB/ParaPowerPython
# Developed by: Fraunhofer IISB

from PPMatLib import PPMatLib

class PPTCM:
    def __init__(self,**kwargs):
        if len(kwargs) == 0:
            self.PottingMaterial = "0"
            self.ParamVar = []
            self.VariableList = []
            self.iFeatures = []
            self.iParams = []
            self.Params = []
            self.iExternalConditions = []
            self.iExpanded = False
            self.iFeaturesTemplate = {
                "x": [],
                "y": [],
                "z": [],
                "Matl": [],
                "Q": [],
                "dx": [],
                "dy": [],
                "dz": [],
                "Desc": []
            }
            self.Version = ""
            
            self.MatLib = PPMatLib()
            self.set_params("Init")
            self.set_features("Init")
            self.set_external_conditions("Init")
        else:
            raise NotImplementedError("kwargs > 0 not implemented yet")
        

    def set_external_conditions(self, input_):
        S = {
            "h_Xminus": [],
            "h_Xplus": [],
            "h_Yminus": [],
            "h_Yplus": [],
            "h_Zminus": [],
            "h_Zplus": [],
            "Ta_Xminus": [],
            "Ta_Xplus": [],
            "Ta_Yminus": [],
            "Ta_Yplus": [],
            "Ta_Zminus": [],
            "Ta_Zplus": [],
            "Tproc": []
        }

        Fields = []
        if input_ == "Init":
            Fields = []
        
        if len(self.iExternalConditions) == 0:
            self.iExternalConditions = S
            self.ExternalConditions = S
            

    def set_features(self, input_):
        F = self.iFeaturesTemplate

        if input_ == "Init":
            FieldsInput = []
            Input = []
        else:
            raise NotImplementedError
        
        FieldsObject = list(F.keys())
        self.iFeatures = Input
        self.Features = Input

    def set_params(self, input_):
        S = {
            'Tinit': [],
            'DeltaT': [],
            'Tsteps': []
        }

        if input_ == "Init":
            Fields = []
        
        if len(self.iParams) == 0:
            self.iParams = S
            self.Params = S
        
        if len(Fields) > 0:
            raise NotImplementedError


    def features(self):
        FeaturesOut = self.iFeatures
        if len(FeaturesOut) == 0:
            FeaturesOut = self.iFeaturesTemplate
        else:
            raise NotImplementedError
        return FeaturesOut
