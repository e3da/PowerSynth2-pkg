# Modified from the original file, which can be found in https://github.com/USArmyResearchLab/ParaPower

from PPMAT import PPMat

class PPMatSolid(PPMat):
    def __init__(self, **kwargs):
        # Default Values
        self.cte = float('nan')
        self.E = float('nan')
        self.nu = float('nan')
        self.k = float('nan')
        self.rho = float('nan')
        self.cp = float('nan')
        self.type = "Solid"
        
        if "type" not in kwargs:
            kwargs["type"] = self.type

        super().__init__(**kwargs)  # Call the parent constructor

        prop_val_pairs = self.prop_val_pairs
        self.prop_val_pairs = {}

        while prop_val_pairs:
            key, element, prop_val_pairs = self.pop(prop_val_pairs)
            
            if not isinstance(key, str):
                raise ValueError("Property Name must be a string!")
            
            if key.lower().startswith("cte"):
                self.cte = element
            elif key.lower().startswith("e"):
                self.E = element
            elif key.lower().startswith("nu"):
                self.nu = element
            elif key.lower().startswith("k"):
                self.k = element
            elif key.lower().startswith("rho"):
                self.rho = element
            elif key.lower().startswith("cp"):
                self.cp = element
            else:
                raise ValueError("Property not recognized!")

    def ParamDesc(self, Param):
        out_text = ''
        lower_param = Param.lower()
        if lower_param == 'cte':
            out_text = 'CTE (1/K)'
        elif lower_param == 'e':
            out_text = "Young's Mod (Pa)"
        elif lower_param == 'nu':
            out_text = "Poisson's Ratio"
        elif lower_param == 'k':
            out_text = 'Conductivity (W/m-K)'
        elif lower_param == 'rho':
            out_text = 'Density (kg/m^3)'
        elif lower_param == 'cp':
            out_text = 'Specific Heat (J/kg-K)'
        else:
            out_text = super().ParamDesc(Param)  # Call the superclass method if not found
        return out_text