import input_params
from jetlag import *
from knownsystems import *
import logOp
import os, re, sys
import traceback
import jetlag_setup

app0 = None
machines_options = []
exec_to_app = {}
all_apps = {}

def clear_entry(entry):
    print("clear_entry:",entry)
    home = os.environ["HOME"]
    fname = home+"/."+entry
    print("remove",fname)
    if os.path.exists(fname):
        os.remove(fname)
    if entry in os.environ:
        del os.environ[entry]

def clear_backend(backend):
    g = re.match(r'{(.*_USER)}', backend["user"])
    if g:
        clear_entry(g.group(1))
    g = re.match(r'{(.*_PASSWORD)}', backend["pass"])
    if g:
        clear_entry(g.group(1))

def gen_data():
    global app0, exec0, machines_options, exec_to_app, all_apps
    mid = input_params.get('middleware')
    if mid is None:
        while mid not in ['Agave', 'Tapis']:
            mid = input("Middleware (Agave/Tapis): ")
        input_params.set('middleware',mid)
    notify = input_params.get('notify','sbrandt@cct.lsu.edu')
    if mid == "Agave":
        backend = backend_agave
    else:
        backend = backend_tapis

    uv = jetlag_setup.uv
    
    machines_options = []
    all_apps = {}
    exec_to_app = {}
    
    jid = uv.values["jetlag_id"]
    val = uv.get_exec()

    perm_data_str = ''
    pems_data = uv.get_app_pems()
    if 'read' in pems_data and pems_data['read'] == True:
        perm_data_str += 'R'
    if 'write' in pems_data and pems_data['write'] == True:
        perm_data_str += 'W'
    if 'execute' in pems_data and pems_data['execute'] == True:
        perm_data_str += 'X'

    machine = uv.values["execm_id"]

    machines_options += [machine]

    app_entry = {
        'exec_sys' : machine,
        'storage_sys' : uv.values["storage_id"],
        'perm' : perm_data_str,
        'queues' : [
            { "name": val["queues"][0]["name"],
              "ppn" : val["queues"][0]["maxProcessorsPerNode"] }
        ],
        'uv':uv
    }
    app0 = uv.fill(uv.values["app_name"]+"-"+uv.values["app_version"])
    exec_to_app[machine] = app0
    exec0 = machine
    all_apps[app0] = app_entry

gen_data()

def get_uv():
    global app0, exec0, machines_options, exec_to_app, all_apps
    middleware = input_params.get('middleware')
    machine_key = 'machine_'+middleware
    exec_sys = input_params.get(machine_key, app0)
    if exec_sys not in exec_to_app:
        exec_sys = exec0
        input_params.set(machine_key, exec_sys)
    app = exec_to_app[exec_sys]
    app_data = all_apps[app]
    uv = app_data["uv"]
    uv.refresh_token()
    return uv

def get_user():
    uv = get_uv()
    return uv.fill(uv.values["sys_user"])
