# Modified from the original file, which can be found in https://github.com/USArmyResearchLab/ParaPower
# Github Repo: https://github.com/FhG-IISB/ParaPowerPython
# Developed by: Fraunhofer IISB

class PPResults:
    Version = 'V1.0'

    def __init__(self, *args):
        self.Model = {}
        self.Case = args[0]
        self.iStates = list(args[1:])
        self.StatesAvail = list(args[1:])

    def setModel(self, Model):
        self.Model = Model

    def addState(self, StateName, StateVal):
        self.iStates.append(StateVal)
        self.StatesAvail.append(StateName)

    def setState(self, StateName, StateVal):
        if StateName == "Thermal":
            self.iStates[0] = StateVal
        elif StateName == "MeltFrac":
            self.iStates[1] = StateVal

    def getState(self, Desc):
        if Desc == "Thermal":
            return self.iStates[0]
        elif Desc == "MeltFrac":
            return self.iStates[1]