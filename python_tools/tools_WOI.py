##########################
### Workin on it tools ###
##########################
# Used as flags to indicate we are working on a specific object (directory)
# useful to launch parallel jobs on different machines with shared memory (cross-machine locking)

# Usage:
# if is_someone_workin_on_it(model_dir_path):
#            warnings.warn(f"This lens, {lens.name} is being worked on, skipping- if not, delete the {workin_on_it} file") 
#            return None
#        set_workin_on_it(lens.model_res_dir,wrk = True)
# [...]
# 
# set_workin_on_it(model_dir_path,wrk = False)

import dill
from pathlib import Path
from python_tools.get_res import load_whatever

workin_on_it = "WOI.dll"
def set_workin_on_it(dir,wrk=True):
    woi_file = Path(dir)/workin_on_it
    with open(woi_file,"wb") as f:
        dill.dump({"workin_on_it":wrk},f)
    
def is_someone_workin_on_it(dir):
    woi_file = Path(dir)/workin_on_it
    if not woi_file.is_file():
        return False
    else:
        return load_whatever(woi_file)["workin_on_it"]

