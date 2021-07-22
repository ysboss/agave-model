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
        sys.stdout = open("spack-log.txt", 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout
        
def emptyListValue(x):
    if not x:
        return "None"
    else:
        return x[0]
    
def emptyListOptions(x):
    if not x:
        return ["None"]
    else:
        return x  

def sendPlugInToServer():
    print("To add models:\n\n1)ssh into the machine you want to use\n2)Install models following the README in the plug-in directory that we are currently sending to your home directory\n3)Rerun the CMR\n")
    print("Sending Plug-In to Server...")
    uv = jetlag_conf.get_uv()
    os.system("rm -fr input.tgz run_dir")
    os.system("mkdir -p run_dir")
    os.system("cp plug-in.tar.gz %s/agave-model/run_dir/" % os.environ["HOME"])
    with HiddenPrint():
        write_env()
        with open("run_dir/sendPlug.sh","w") as v:
            print("#!/bin/bash", file=v)
            print("tar -xvf plug-in.tar.gz -C $HOME", file=v)
        os.system("chmod 755 run_dir/get-versions.sh")
        with open("run_dir/runapp.sh","w") as fd:
            print("singularity exec $SING_OPTS --pwd $PWD $IMAGE bash -l ./sendPlug.sh", file=fd)
        os.system("tar czvf input.tgz run_dir")
        jobid = uv.run_job("sendingPlugIn", nx=4, ny=4, nz=1, jtype="queue", run_time="1:00:00")
        jobid.wait()
    print("Done!")
    
def getMachineFiles():
    uv = jetlag_conf.get_uv()
    os.system("rm -fr input.tgz run_dir")
    os.system("mkdir -p run_dir")
    print("Getting List of Models...")
    print("This may take a few minutes...")
    with HiddenPrint():
        write_env()
        with open("run_dir/get-versions.sh","w") as v:
            print("#!/bin/bash", file=v)
            print("mkdir machineFiles", file=v)
            print("cp /build-dir/json/* machineFiles", file=v)
            print("cp /build-dir/spack-info.txt machineFiles", file=v)
            #print("cp /JSON/* machineFiles")
            print("tar -czvf machineFiles.tar.gz machineFiles", file=v)
        os.system("chmod 755 run_dir/get-versions.sh")
        with open("run_dir/runapp.sh","w") as fd:
            print("singularity exec $SING_OPTS --pwd $PWD $IMAGE bash ./get-versions.sh", file=fd)
        os.system("tar czvf input.tgz run_dir")
        jobid = uv.run_job("get_models_and_packs", nx=4, ny=4, nz=1, jtype="queue", run_time="1:00:00")
        jobid.wait()
        uv.get_file(jobid, "run_dir/machineFiles.tar.gz",as_file="machineFiles.tar.gz")
        print("Done!")
    
def getModelsAndPacks():
    
    # Alternative Method
    # models = os.listdir("/home/jovyan/agave-model/models")
    # models = [x.upper() for x in models]
    
    getMachineFiles()
    
    machinePath = "%s/agave-model/machineFiles" % os.environ["HOME"]
    
    os.system("rm -rf %s/agave-model/machineFiles" % os.environ["HOME"])
    
    os.system("tar -xvf %s/agave-model/machineFiles.tar.gz -C %s/agave-model/" % (os.environ["HOME"], os.environ["HOME"]))
    os.system("rm %s/agave-model/machineFiles.tar.gz" % os.environ["HOME"])
    
    path = os.environ["HOME"]+"/agave-model/machineFiles/"
    name_list = []
    package_list = []
    
    if os.path.isfile(os.environ["HOME"]+"/agave-model/machineFiles/*.json") or os.path.isfile(os.environ["HOME"]+"/agave-model/machineFiles/spack-info.txt"):
    
        for filename in glob.glob(os.path.join(path, '*.json')):
            with open(os.path.join(os.getcwd(), filename), 'r') as f:
                data = json.loads(f.read())          
                name_list.append(data['name'])
                package_list.append(data['package'] + '@' + data['version'])
                
    return tuple(name_list), tuple(package_list)

def packSplit(pack):
    temp = pack.split('@')
    return temp[0]
        
def get_versions(model):

    VERSIONS = []

    if os.path.isfile(os.environ["HOME"]+"/agave-model/machineFiles/spack-info.txt"):
        p = open("%s/agave-model/machineFiles/spack-info.txt" % os.environ["HOME"]).read()
        for g in re.finditer(r'(\w+)@([\d.]+)', p):
            package = g.group(1)
            version = g.group(2)

            if package == model.lower():
                VERSIONS.append(version)

    return VERSIONS
