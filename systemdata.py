import re
from command import cmd
import json
import pickle
import os


def load(reload=False,trace=False):
    if not reload:
        try:
            with open("app-data.pickle","rb") as fd:
                return pickle.load(fd)
        except:
            pass

    # Get the username
    with open(os.environ["HOME"]+"/.agave/current","r") as fd:
        jd = json.loads(fd.read())
        user = jd["username"]

    all_apps = {}

    out = cmd('apps-list',show=False,trace=trace)
    for line in out["stdout"]:
        app = line
        if not re.match(r'crcollab',app):
            continue

        # Get permissions for the app
        pout = cmd("apps-pems-list -v -u "+user+" "+app,show=False,trace=trace)
        pdata = json.loads(" ".join(pout["stdout"]))
        perm = pdata["permission"]
        perms = ""
        if perm["read"]:
            perms += "R"
        if perm["write"]:
            perms += "W"
        if perm["execute"]:
            perms += "X"

        appdata = cmd('apps-list -V '+app,show=False,trace=True)
        jtxt = " ".join(appdata["stdout"])
        jd = json.loads(jtxt)
        jd = jd["result"]

        exec_sys=jd["executionSystem"]
        storage_sys=jd["deploymentSystem"]
        execdata = cmd('systems-list -v '+exec_sys,show=False,trace=trace)
        jd2 = json.loads(" ".join(execdata["stdout"]))
        queues = []
        for q in range(len(jd2["queues"])):
            name = jd2["queues"][q]["name"]
            ppn = jd2["queues"][q]["maxProcessorsPerNode"]
            queues += [{"name":name, "ppn":ppn}]
        all_apps[app] = {
            "perm":perms,
            "exec_sys":exec_sys,
            "storage_sys":storage_sys,
            "queues":queues
        }


    with open("app-data.pickle","wb") as fd:
        pickle.dump(all_apps,fd)

    return all_apps

def display():
    d = load(reload=True)
    print("Applications you have access to:")
    access = 0
    for app in d:
        if d[app]["perm"] in ["RWX", "RX"]:
            print("  -",app)
            access += 1
    if access == 0:
        print("  None")
    print()

    print("Applications you don't have access to:")
    noaccess = 0
    for app in d:
        if d[app]["perm"] not in ["RWX", "RX"]:
            print("  -",app)
            noaccess += 1
    if noaccess == 0:
        print("  None")
    print()

    print("Please contact sbrandt@cct.lsu.edu for questions")
