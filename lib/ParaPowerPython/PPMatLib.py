# Modified from the original file, which can be found in https://github.com/USArmyResearchLab/ParaPower
# Github Repo: https://github.com/FhG-IISB/ParaPowerPython
# Developed by: Fraunhofer IISB

from PPMAT import PPMat
import numpy as np

class PPMatLib:
    def __init__(self, *args):
        self.GUIModFlag = False
        self.ParamVar = []
        self.ParamTable = []
        
        self.iParamList = []
        self.iFilename = ''
        self.iMatTypeList = []
        self.iNameList = []
        self.iMatObjList = []
        self.iPropVals=[]
        self.ErrorText = ''
        
        if len(args) >= 1 and isinstance(args[0], PPMat):
            for mat in args:
                if isinstance(mat, PPMat):
                    self.AddMatl(mat)
                else:
                    self.AddError('For PPMatLib(Mat1, Mat2, Mat3) form all arguments must be a material class.')
                    self.AddError(f'Argument {type(mat)} is of type')
        elif len(args) == 1 and isinstance(args[0], PPMatLib):
            old_lib = args[0]
            for i in range(old_lib.NumMat):
                self.AddMatl(old_lib.GetMatNum(i))

        self.ShowErrorText()
    
    @property
    def NumMat(self):
        return len(self.iMatObjList)

    @property
    def Params(self):
        return self.iParamList

    @property
    def Source(self):
        return self.iSource

    @Source.setter
    def Source(self, text):
        self.iSource = text

    def GetParam(self, Param):
        OutParam = []
        IsNumericParam = True
        Param = Param.lower()
        for Imat in range(self.NumMat):
            MatObj = self.GetMatNum(Imat)
            if hasattr(MatObj, Param):
                value = getattr(MatObj, Param)
                OutParam.append(value)
                if not isinstance(value, (int, float, np.number)):
                    IsNumericParam = False
            else:
                OutParam.append(np.nan)
        if IsNumericParam:
            OutParam = np.array(OutParam)
        OutParam = np.reshape(OutParam, (-1, 1))
        return OutParam
    
    def GetParamVector(self, Param):
        Param = Param.lower()
        if len(self.iPropVals) == 0:
            self.PopulateProps()
        try:
            Iprop = self.iParamList.index(Param)
        except ValueError:
            raise ValueError(f"Parameter {Param} not found in parameter list.")
        
        OutParamVec = self.iPropVals[:, Iprop]
        if isinstance(OutParamVec, np.ndarray) and OutParamVec.dtype == 'O':
            OutParamVec = np.array([item for sublist in OutParamVec for item in sublist])
        OutParamVec = np.reshape(OutParamVec, (-1, 1))
        return OutParamVec

    def MatList(self):
        M = []
        for i in range(len(self.iMatObjList)):
            M.append(self.iMatObjList[i].name)
        return M
    
    def ClearProps(self):
        self.iPropVals = []
    
    def GetMatNum(self, MatNum):
        if MatNum < self.NumMat:
            return self.iMatObjList[MatNum]
        else:
            raise ValueError("Material Number does not exist!")
        
    def PopulateProps(self):
        base_props = ["name", "max_plot", "type"]
        iPropValsBuf = np.full((self.NumMat, len(self.iParamList)), np.nan)
        iParamList = self.iParamList
        if (self.iParamList[0].lower() == base_props[0].lower() and
            self.iParamList[1].lower() == base_props[1].lower()):
            for Imat in range(self.NumMat):
                ThisMat = self.GetMatNum(Imat)
                ThisMatProps = [
            "cte", "E","nu", "k", "rho", "cp", "max_plot", "name", "type"
        ]
                for Iprop in range(len(base_props), len(iParamList)):
                    if any(prop == iParamList[Iprop] for prop in ThisMatProps):
                        iPropValsBuf[Imat][Iprop] = getattr(ThisMat, iParamList[Iprop])
            self.iPropVals = iPropValsBuf
    
    def UpdateInternalVars(self):
        MatTypeList = []
        MatNameList = []
        MatParmList = []

        for I in range(self.NumMat):
            TempMat = self.GetMatNum(I)
            MatTypeList.append(TempMat.type)
            MatNameList.append(TempMat.name)
            TempParmList = TempMat.ParamList()
            MatParmList += TempParmList
        
        MatTypeList = list(set(MatTypeList))
        MatParmList = list(set(MatParmList))

        abstract_fields = ["name", "max_plot", "type"]

        for I in range(len(abstract_fields)):
            MatParmList = [param for param in MatParmList if param.lower() != abstract_fields[I].lower()]

        self.iParamList = abstract_fields + MatParmList
        self.iMatTypeList = MatTypeList
        self.iNameList = MatNameList
        self.PopulateProps()

    def AddMatl(self, PPMatObject):
        if not PPMatObject:
            raise ValueError("Empty Material Object!")
        elif PPMatObject.name in self.iNameList:
            raise ValueError(f"Material {PPMatObject.name} already exists in Library!")
        elif PPMatObject.type == "Abstract":
            raise ValueError(f"Materials of type Abstract cannot be added to the library!")
        
        self.iMatObjList.append(PPMatObject)
        self.ClearProps()
        self.UpdateInternalVars()

    def ShowErrorText(self):
        if self.ErrorText:
            print(self.ErrorText)
            self.AddError()