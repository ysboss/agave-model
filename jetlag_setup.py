import jetlag as j
from gui_fun import gui_fun, settings
uv = j.Universal()
settings(uv.loadf,{"passw":"password","utype":["tapis","agave"]})
r=gui_fun(uv.loadf)

def query_jetlag_id(jid):
	return jid

cmr_jetlag_id = None
def set_jetlag_id(jid):
    uv.load(
        uv.values["backend"],
        uv.values["notify"],
        jid)
    print("jetlag id set to:",uv.values["jetlag_id"])

def on_load(_):
    jetlag_id = uv.values["jetlag_id"]
    if jetlag_id is None or jetlag_id == "unknown":
        jids = uv.jetlag_ids()
        if len(jids)==0:
            print("You are not authorized to use JetLag. Contact sbrandt@cct.lsu.edu")
        else:
            print("You have not supplied a JetLag id... querying")
            settings(query_jetlag_id,{"jid":jids})
            res = gui_fun(query_jetlag_id)
            res.add_listener(set_jetlag_id)

r.add_listener(on_load)
