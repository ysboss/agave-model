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

def getModelsAndPacks():
    
    uv = jetlag_conf.get_uv()
    os.system("rm -fr input.tgz run_dir")
    os.system("mkdir -p run_dir")
    print("Retrieving List of Models...")
    print("This may take a few minutes...")
    if True: #with HiddenPrint():
        write_env()
        os.system("tar czvf input.tgz run_dir")
        jobid = uv.run_job("get_models_and_packs", nx=1, ny=1, nz=1, jtype="queue", run_time="1:00:00",script_name="getModelsPacks")
        jobid.wait()
        uv.get_file(jobid, "run_dir/machineFiles.tar.gz",as_file="machineFiles.tar.gz")
                
   
    #machinePath = "%s/agave-model/machineFiles" % os.environ["HOME"]
    
    os.system("rm -rf %s/agave-model/machineFiles" % os.environ["HOME"])
    os.system("tar -xvf %s/agave-model/machineFiles.tar.gz -C %s/agave-model/" % (os.environ["HOME"], os.environ["HOME"]))
    os.system("rm %s/agave-model/machineFiles.tar.gz" % os.environ["HOME"])   
    
    path = []
    path.append(os.environ["HOME"]+"/agave-model/machineFiles/")
    path.append(os.environ["HOME"]+"/agave-model/JSONFiles/")
    
    name_list = []
    package_list = []
    
    if os.path.isfile(os.environ["HOME"]+"/agave-model/machineFiles/*.json") and os.path.isfile(os.environ["HOME"]+"/agave-model/machineFiles/spack-info.txt") or os.path.isdir(os.environ["HOME"]+"/agave-model/JSONFiles"):
        
        for x in range(2):
            for filename in glob.glob(os.path.join(path[x], '*.json')):
                with open(os.path.join(os.getcwd(), filename), 'r') as f:
                    data = json.loads(f.read())          
                    name_list.append(data['name'])
                    package_list.append(data['package'] + '@' + data['version'])

        print("Done!")
        
    else:
        print("Error with retrieving certain files from server!")
    
    return tuple(name_list), tuple(package_list)
