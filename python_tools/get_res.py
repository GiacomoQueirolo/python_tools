import os
import json,pickle,dill
def load_whatever(name):
    try:        
        with open(name, 'rb') as f:
            data = dill.load(f)
    except:
        try:
            with open(name,'rb') as f:
                data = pickle.load(f)
        except:
            try:
                with open(name, 'r') as f:
                    data = json.load(f)
            except:
                with open(name, 'r') as f:
                    data = f.readlines()
                data = [data_l.replace(",\n","") for data_l in data]   
    return data


def get_path_str(path,path_base=None):
    path_str = str(path)
    if path_base:
        path_str = path_str.replace(str(path_base),"(base)") 
    return path_str
    
def _LoadClass(path,verbose=True,path_base=None):
    Cl = load_whatever(path)
    if verbose:
        print(f"Loaded {get_path_str(path,path_base=path_base)}:\n{Cl}")
    return Cl
    

def LoadClass(path,verbose=True,LoadFnc=_LoadClass,path_base=None):
    pth_str = get_path_str(path,path_base=path_base)
    if os.path.isfile(path):
        print(f"File {pth_str} is present")
        try:
            return LoadFnc(path=path,verbose=verbose,path_base=path_base)
        except Exception as e:
            print(f"But failed to load: \n{str(e)}")
            return False
    else:
        print(f"File {pth_str} not present")
        return False
