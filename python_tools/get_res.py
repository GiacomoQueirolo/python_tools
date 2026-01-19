import os
import json,pickle,dill
def load_whatever(name):
    try:        
        with open(name, 'rb') as f:
            data = dill.load(f)
    except:
        try:
            with open(name, 'r') as f:
                data = json.load(f)
        except:
            try:
                with open(name,'rb') as f:
                    data = pickle.load(f)
            except:
                with open(name, 'r') as f:
                    data = f.readlines()
                data = [data_l.replace(",\n","") for data_l in data]   
    return data


def _LoadClass(path,verbose=True):
    Cl = load_whatever(path)
    if verbose:
        print(f"Loaded {path}:\n{Cl}")
    return Cl
    

def LoadClass(path,verbose=True,LoadFnc=_LoadClass):
    if os.path.isfile(path):
        print("File "+path+" is present")
        try:
            return LoadFnc(path=path,verbose=verbose)
        except Exception as e:
            print("But failed to load: \n"+str(e))
            return False
    else:
        print("File not present")
        return False

