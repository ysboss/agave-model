from subprocess import Popen, PIPE
import re
import glob
import json
from command import cmd
from write_env import write_env
import jetlag_conf
import os, sys
import input_params

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

def getModelsAndPacks(update_flag):
    
    if (input_params.get("last_jid") != jetlag_conf.get_uv().jetlag_id) or update_flag:
        uv = jetlag_conf.get_uv()
        cmd("rm -fr input.tgz run_dir")
        cmd("mkdir -p run_dir")
        print("Retrieving List of Models...")
        print("This may take a few minutes...")
        if True: #with HiddenPrint():
            write_env()
            cmd("tar czvf input.tgz run_dir")
            job = uv.run_job("get_models_and_packs", nx=1, ny=1, nz=1, jtype="queue", run_time="1:00:00",script_name="getModelsPacks")
            job.wait()
            try:
                uv.get_file(job, "run_dir/machineFiles.tar.gz",as_file="machineFiles.tar.gz")
            except:
                ###
                print("Config failed: Is remote machine configured properly?")
                print(job.err_output())
                ###


        #machinePath = "%s/agave-model/machineFiles" % os.environ["HOME"]

        cmd("rm -rf %s/agave-model/machineFiles" % os.environ["HOME"])
        cmd("tar -xvf %s/agave-model/machineFiles.tar.gz -C %s/agave-model/" % (os.environ["HOME"], os.environ["HOME"]))
        cmd("rm %s/agave-model/machineFiles.tar.gz" % os.environ["HOME"])   
    
    path = os.environ["HOME"]+"/agave-model/machineFiles/"
    
    name_list = []
    package_list = []
    
    if os.path.isdir(os.environ["HOME"]+"/agave-model/machineFiles/"):      

        for filename in glob.glob(os.path.join(path, '*.json')):
            with open(os.path.join(os.getcwd(), filename), 'r') as f:
                data = json.loads(f.read())          
                name_list.append(data['name'])
                package_list.append(data['package'] + '@' + data['version'])

        if input_params.get("last_jid") != jetlag_conf.get_uv().jetlag_id:
            print("Done!")
        
    else:
        print("Error with retrieving certain files from server!")
    
    return tuple(name_list), tuple(package_list)
