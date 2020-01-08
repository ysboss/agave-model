from jetlag import *
from knownsystems import *
import input_params

app0 = None
machines_options = []
exec_to_app = {}
all_apps = {}

def gen_data():
    global app0, machines_options, exec_to_app, all_apps
    w = input_params.get('middleware')
    email = input_params.get('email','sbrandt@cct.lsu.edu')
    if w == "Agave":
        backend = backend_agave
    else:
        backend = backend_tapis
    uv = Universal()
    uv.load(
        backend,
        email,
        'shelob'
    )
    uv.refresh_token()
    
    machines_options = []
    all_apps = {}
    exec_to_app = {}
    
    for m in uv.get_meta('system-config-*'):
        val = m["value"]
    
        uv2 = Universal()
        uv2.init(
            backend=uv.values["backend"],
            email=email,
            **val)
    
        perm_data_str = ''
        pems_data = uv2.get_app_pems()
        if 'read' in pems_data and pems_data['read'] == True:
            perm_data_str += 'R'
        if 'write' in pems_data and pems_data['write'] == True:
            perm_data_str += 'W'
        if 'execute' in pems_data and pems_data['execute'] == True:
            perm_data_str += 'X'
    
        machine = uv2.values["execm_id"]
    
        machines_options += [machine]
    
        app_entry = {
            'exec_sys' : machine,
            'storage_sys' : uv2.values["storage_id"],
            'perm' : perm_data_str,
            'queues' : [
                { "name": val["queue"],
                  "ppn" : val["max_procs_per_node"] }
            ],
            'uv':uv2
        }
        app0 = uv2.fill(uv2.values["app_name"]+"-"+uv2.values["app_version"])
        all_apps[app0] = app_entry
        exec_to_app[machine] = app0

gen_data()

def get_uv():
    exec_sys = input_params.get('machine',app0)
    app = exec_to_app[exec_sys]
    app_data = all_apps[app]
    uv = app_data["uv"]
    uv.refresh_token()
    return uv
