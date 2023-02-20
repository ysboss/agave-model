#!/usr/bin/env python3
import yaml
import json
import os
from subprocess import Popen, PIPE
from termcolor import colored

def do_cmd(cmd,inp=None):
    print(colored('cmd:',"green"),cmd)
    if inp is None:
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        out, err = p.communicate()
    else:
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        out, err = p.communicate(inp)
    print(colored(err,"red"),end='')
    return out, err

home = os.environ["HOME"]
spack = os.path.join(home, ".spack", "packages.yaml")

## CONFIGURE UPSTREAMS
#for base in ["", "/usr/local"]:
#    upstreams=f"""
#upstreams:
#  spack-instance-1:
#    install_tree: {base}/spack/opt/spack
#    modules:
#        tcl: {base}/spack/share/spack/modules
#"""
#    upstr = os.path.join(home, ".spack", "upstreams.yaml")
#    if os.path.exists(f"{base}/spack/opt/spack"):
#        with open(upstr,"w") as fd:
#            print(upstreams, file=fd, end='')
#            break
#    elif os.path.exists(upstr):
#        os.remove(upstr)
## END CONFIGURE UPSTREAMS

## CONFIGURE PACKAGES
if os.path.exists(spack):
    with open(spack, "r") as fd:
        spec = yaml.safe_load(fd)
else:
    spec = {}

#with open("p.json","w") as fd:
#    print(json.dumps(spec),file=fd,end='')

out, err = do_cmd(["spack","find","--json"])
jdata = json.loads(out)

versions = {}
targets = {}
for k in jdata:
    name = k["name"]
    version = k["version"]
    if name not in versions:
        versions[name] = []
    if version not in versions[name]:
        versions[name] = [version] + versions[name]
    target = k["arch"]["target"]["name"]
    if name not in targets:
        targets[name] = []
    if target not in targets[name]:
        targets[name] = [target] + targets[name]

if "packages" not in spec:
    spec["packages"] = {}

pkgs = spec["packages"]
if "all" not in pkgs:
    spec["packages"]["all"] = {}
if "providers" not in pkgs["all"]:
    spec["packages"]["all"]["providers"] = {}
spec["packages"]["all"]["providers"]["mpi"] = ["mpich", "openmpi"]

for p in versions:
    if p not in spec["packages"]:
        spec["packages"][p] = {}
    spec["packages"][p]["version"] = versions[p]
for t in targets:
    if t not in spec["packages"]:
        spec["packages"][t] = {}
    spec["packages"][t]["target"] = targets[t]

with open(spack,"w") as fd:
    yaml.dump(spec, fd)
