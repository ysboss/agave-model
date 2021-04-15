from jetlag import RemoteJobWatcher
from subprocess import Popen, PIPE
import re
import glob
import json
from command import cmd
from write_env import write_env
import jetlag_conf
import os, sys
        
class HiddenPrint:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open("spack-log.txt", 'a')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout
    
    
def getModels():
    print("Getting List of Models...")
    path = os.environ["HOME"]+"/agave-model/science-models/JsonFiles"
    name_list = []
    package_list = []
    for filename in glob.glob(os.path.join(path, '*.json')):
        with open(os.path.join(os.getcwd(), filename), 'r') as f:
            data = json.loads(f.read())          
            name_list.append(data['name'])
            package_list.append(data['package'])
    return tuple(name_list), tuple(package_list)
# Get list of all models we need to have in the CMR    
   

def get_versions(model):

    VERSIONS = []

    p = open("spack-info.txt").read()
    for g in re.finditer(r'(\w+)@([\d.]+)', p):
        package = g.group(1)
        version = g.group(2)

        if package == model:
            VERSIONS.append(version)

    return VERSIONS
# Function to get the
# different versions of
# spack packages for
# a given model


def findNewModels(packs):
    
    packs_list = list(packs)
    p = open("spack-info.txt").read()
    for g in re.finditer(r'(\w+)@([\d.]+)', p):
        knownPack = g.group(1)
        if knownPack in packs_list:
            packs_list.remove(knownPack)
    return packs_list
        

def gen_spack_pack_list():
    uv = jetlag_conf.get_uv()
    os.system("rm -fr input.tgz run_dir")
    os.system("mkdir -p run_dir")
    with HiddenPrint():
        write_env()
        with open("run_dir/get-versions.sh","w") as v:
            print("#!/bin/bash", file=v)
            print("source /spack/share/spack/setup-env.sh", file=v)
            print("spack find > spack-info.txt", file=v)
        os.system("chmod 755 run_dir/get-versions.sh")
        with open("run_dir/runapp.sh","w") as fd:
            print("singularity exec $SING_OPTS --pwd $PWD $IMAGE bash ./get-versions.sh", file=fd)
        os.system("tar czvf input.tgz run_dir")
        jobid = uv.run_job("get_model_versions", nx=4, ny=4, nz=1, jtype="queue", run_time="1:00:00")
        uv.wait_for_job(jobid)
        uv.get_file(jobid, "run_dir/spack-info.txt",as_file="spack-info.txt")
    