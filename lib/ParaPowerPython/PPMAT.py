# Modified from the original file, which can be found in https://github.com/USArmyResearchLab/ParaPower

class PPMat:
    def __init__(self, **kwargs):
        self.name = ''
        self.max_plot = True
        self.type = 'Abstract'
        self.prop_val_pairs = {}
    
        prop_val_pairs = kwargs
        while prop_val_pairs:
            key, element, prop_val_pairs = self.pop(prop_val_pairs)
            
            if not isinstance(key, str):
                raise ValueError("Key should be a string!")
            
            if key.lower().startswith("name"):
                self.name = element
            elif key.lower().startswith("type"):
                if isinstance(element,str):
                    self.type = element
                else:
                    raise ValueError("Material Type must be a string!")
            else:
                self.prop_val_pairs[key] = element
    
    def ParamList(self):
        return [
            "cte", "E","nu", "k", "rho", "cp", "max_plot"
        ]
    
    def pop(self, _dict_):
        key_to_pop = list(_dict_.keys())[0]
        element = _dict_.pop(key_to_pop)
        return key_to_pop, element, _dict_

    #@staticmethod
    def valid_chars(name: str) -> bool:
        return all(c.isalnum() or c == '_' for c in name)

    @staticmethod
    def check_logical(value):
        if isinstance(value, bool):
            return value
        if value in ['true', 't', True]:
            return True
        elif value in ['false', 'f', False]:
            return False
        raise ValueError('Value must be a boolean.')

    def param_list(self, include_name_type=False):
        params = [p for p in dir(self) if not p.startswith('_') and p not in ['name', 'type']]
        if include_name_type:
            return ['Name', 'Type'] + params
        return params

    def param_desc(self, param):
        descs = {
            'name': 'Name',
            'type': 'Type',
            'max_plot': 'Show in Pk Plots (T/F)'
        }
        return descs.get(param.lower(), '')