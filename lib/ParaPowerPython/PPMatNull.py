# Modified from the original file, which can be found in https://github.com/USArmyResearchLab/ParaPower
# Github Repo: https://github.com/FhG-IISB/ParaPowerPython
# Developed by: Fraunhofer IISB

from PPMatSolid import PPMatSolid
import numpy as np

class PPMatNull(PPMatSolid):
    def __init__(self, **kwargs):
        Type = "Null"

        if "type" not in kwargs:
            kwargs["type"] = Type
        
        super().__init__(**kwargs)

        self.cte = 0
        self.E = 0
        self.nu = 0
        self.k = np.inf
        self.rho = 0
        self.cp = 0
        



