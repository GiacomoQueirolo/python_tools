import os
import json
import inspect
import numpy as np
import pathlib as pth

def get_dir_basename(FILE):
    # simple utility function to obtain directory and name of file
    dir  = os.path.dirname(FILE)+"/"
    if dir=="/":
        dir="./"
    base = os.path.basename(FILE)
    return dir, base
    
def convert_error_to_warning(exception):
    warning = RuntimeWarning(*exception.args)
    warning.with_traceback(exception.__traceback__)
    return warning
    
def extract_xy_from_file(file_name,index_x=1,index_y=2):
    """
    Extracts X_IMAGE (index_x_nd column) and Y_IMAGE (index_y_nd column) from a data file.

    Parameters:
        file_path (str): Path to the input file.

    Returns:
        x (numpy.ndarray): Array of x coordinates.
        y (numpy.ndarray): Array of y coordinates.
    """
    data = []

    with open(file_name, "r") as f:
        for line in f:
            # Skip comment lines
            if line.strip().startswith("#"):
                continue
            
            # Split and convert to float
            values = line.split()
            if len(values) >= max([index_x,index_y])+1:  # Ensure there are enough columns
                x_value = float(values[index_x])  # 2nd column
                y_value = float(values[index_y])  # 3rd column
                data.append((x_value, y_value))

    # Convert to numpy arrays
    x, y = np.array(data).T  
    return x, y
    
def Read_Two_Column_File(file_name):
    # simplified version of extract_xy_from_file
    # kept for simplicity/historical reason
    # and for paring w Write_Two_Column_File
    with open(file_name, 'r') as data:
        x = []
        y = []
        for line in data.readlines():
            if line[0]== "#":
                continue
            p = line.split()
            x.append(float(p[0]))
            y.append(float(p[1]))

    return np.array(x),np.array(y)

def Read_Column_File(file_name):
    """
    Generalised version of Read_Two_Column_File 
    for any number of columns
    """
    with open(file_name, 'r') as data:
        read_data = None
        for line in data.readlines():
            if line[0]== "#":
                continue
            p = line.split()
            if read_data is None:
                read_data = [[] for _ in range(len(p))]
            #print(read_data)
            for ip,pp in enumerate(p):
                read_data[ip].append(float(pp))
    return np.array(read_data)


def Write_Two_Column_File(x,y,out_file):
    assert len(x)==len(y)
    with open(out_file,"w") as file:
        for i in range(len(x)):
            file.write(str(x[i])+"   "+str(y[i])+"\n")
    print("Saved "+out_file)
    return 0

def mkdir(dir_path,parents=True):
    pth.Path(dir_path).mkdir(parents=parents, exist_ok=True)


def save_json(data,filename):
    data = np.array(data).tolist()
    print("Saving "+filename)
    with open(filename, 'w') as f: 
        json.dump(data, f)
        
# get def. argument of function
def get_default_args(func):
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


def short_SciNot(value):
    #short scientific notation
    try:
        unit  = value.unit
        value = value.value
    except:
        unit = None
        pass
    val_str = f"{value:.2e}"
    if unit:
        val_str+= "["+str(unit)+"]"
    return val_str



def to_dimless(variable,verbose=False):
    # check if has unit and convert to dimensionless
    try:
        variable.value
        if verbose:
            print("Original unit",variable.unit)
        return variable.value
    except:
        # variable is already dimensionless
        return variable
        
def ensure_unit(variable,unit):
    # check if has unit
    try:
        # if has unit, verify it's the same
        if not variable.unit==unit:
            return variable.to(unit) 
        else:
            return variable
    except AttributeError:
        # variable is dimensionless
        return variable*unit

