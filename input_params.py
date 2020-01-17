import os
import re

home = os.environ["HOME"]
params_dir = home+"/.model_params"

pglobals = {}

def set(name,value):
    global pglobals, home, params_dir
    os.makedirs(params_dir, exist_ok=True)
    param_dir = params_dir+"/"+name+".txt"
    with open(param_dir, "w") as fd:
        print(value,file=fd)
    pglobals[name] = value

def get(name,default=None):
    global pglobals, home, params_dir
    if name in pglobals:
        return pglobals[name]
    param_dir = params_dir+"/"+name+".txt"
    if os.path.exists(param_dir):
        with open(param_dir,"r") as fd:
            value = fd.read().strip()
    else:
        value = default
        set(name, value)
    pglobals[name] = value
    return value
