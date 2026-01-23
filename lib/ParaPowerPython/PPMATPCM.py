# Modified from the original file, which can be found in https://github.com/USArmyResearchLab/ParaPower
# Github Repo: https://github.com/FhG-IISB/ParaPowerPython
# Developed by: Fraunhofer IISB

import numpy as np
from PPMatSolid import PPMatSolid

class PPMATPCM(PPMatSolid):
    def __init__(self, **kwargs):
        self.type='PCM'
        self.k_l = np.nan
        self.rho_l = np.nan
        self.cp_l = np.nan
        self.lf = np.nan
        self.tmelt = np.nan
        kwargs["type"] = self.type

        super().__init__(**kwargs)

        PropValPairs = self.prop_val_pairs
        self.prop_val_pairs = []