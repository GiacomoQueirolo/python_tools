import os
import json
import base64
import hashlib
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
    val_str = f"{float(value):.2e}"
    if unit:
        val_str+= "["+str(unit)+"]"
    return val_str
    """
    val = "%.e"%(float(value))
    val_str = str(val).replace("+","")
    ant_val_str,post_val_str = val_str.split("e")
    power_sign = ""
    if post_val_str[0]=="-":
        power_sign   = "-"
        post_val_str = post_val_str[1:]
    val_str = ant_val_str+"e"+power_sign+post_val_str.lstrip("0")
    
    """


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

def to_uid(obj, digits=None) -> int:
    # convert any object (ideally: identity) into hash
    if type(obj)==dict:
        obj = sorted(obj.items())
    serialised = repr(obj).encode()
    h = hashlib.md5(serialised).hexdigest()
    if digits:
        h = h[:digits]
    return int(h, 16)


def to_uid_base64(obj, n_chars=6) -> str:
    # convert any object (ideally: identity) into base64 hash
    if type(obj)==dict:
        obj = sorted(obj.items())
    h = hashlib.md5(repr(obj).encode()).digest()  
    b64 = base64.urlsafe_b64encode(h).decode()    
    if n_chars:
        b64 = b64[:n_chars]
    return b64
    

# obtained with Claude
def dict_equal(a, b, rtol=1e-9, atol=0.0, _path="",ret_diff_list=False):
    """
    Recursively compare two objects (dicts, lists, arrays, scalars).
    Returns (True, []) if equal, (False, [list of differing paths]) if not.

    Parameters
    ----------
    a, b   : objects to compare
    rtol   : relative tolerance for float comparison
    atol   : absolute tolerance for float comparison
    _path  : internal, tracks key path for reporting
    ret_diff_list: bool, if False return is only True or False
    """
    diffs = []

    # ── both dicts ────────────────────────────────────────────────────────────
    if isinstance(a, dict) and isinstance(b, dict):
        keys_a, keys_b = set(a.keys()), set(b.keys())
        for k in keys_a - keys_b:
            diffs.append(f"{_path}.{k}: only in first")
        for k in keys_b - keys_a:
            diffs.append(f"{_path}.{k}: only in second")
        for k in keys_a & keys_b:
            _, sub = dict_equal(a[k], b[k], rtol=rtol, atol=atol,
                                _path=f"{_path}.{k}")
            diffs.extend(sub)

    # ── both lists/tuples ─────────────────────────────────────────────────────
    elif isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        if len(a) != len(b):
            diffs.append(f"{_path}: length {len(a)} vs {len(b)}")
        else:
            for i, (ai, bi) in enumerate(zip(a, b)):
                _, sub = dict_equal(ai, bi, rtol=rtol, atol=atol,
                                    _path=f"{_path}[{i}]")
                diffs.extend(sub)

    # ── numpy arrays ──────────────────────────────────────────────────────────
    elif isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        a_arr = np.asarray(a)
        b_arr = np.asarray(b)
        if a_arr.shape != b_arr.shape:
            diffs.append(f"{_path}: shape {a_arr.shape} vs {b_arr.shape}")
        elif not np.allclose(a_arr, b_arr, rtol=rtol, atol=atol, equal_nan=True):
            n_diff = np.sum(~np.isclose(a_arr, b_arr, rtol=rtol, atol=atol,
                                        equal_nan=True))
            diffs.append(f"{_path}: arrays differ in {n_diff}/{a_arr.size} elements")

    # ── floats ────────────────────────────────────────────────────────────────
    elif isinstance(a, float) and isinstance(b, float):
        if not (np.isnan(a) and np.isnan(b)):
            if not np.isclose(a, b, rtol=rtol, atol=atol):
                diffs.append(f"{_path}: {a} vs {b}")

    # ── type mismatch ─────────────────────────────────────────────────────────
    elif type(a) != type(b):
        diffs.append(f"{_path}: type {type(a).__name__} vs {type(b).__name__}")

    # ── everything else (int, str, bool, None, ...) ───────────────────────────
    else:
        if a != b:
            diffs.append(f"{_path}: {a!r} vs {b!r}")

    equal = len(diffs) == 0
    if ret_diff_list:
        return equal, diffs
    else:
        return equal
