from jetlag import *
from knownsystems import *

uv = Universal()
uv.load(
    backend_agave,
    'sbrandt@cct.lsu.edu',
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
        email=uv.values["email"],
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
