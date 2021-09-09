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

    ver = []
    VERSIONS = []
    paths = []
    
    paths.append(os.environ["HOME"]+"/agave-model/science-models/defaultVersions.txt")
    paths.append(os.environ["HOME"]+"/agave-model/machineFiles/spack-info.txt")
    
    for p in paths:
        if os.path.isfile(p):
            p = open(p).read()
            for g in re.finditer(r'(\w+)@([\d.]+)', p):
                package = g.group(1)
                version = g.group(2)

                if package == model.lower():
                    ver.append(version)

    [VERSIONS.append(x) for x in ver if x not in VERSIONS]
    return VERSIONS

def getModelsAndPacks(update_flag):
    
    #(input_params.get("last_jid") != jetlag_conf.get_uv().jetlag_id)
    
    if update_flag:
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
    
    paths = []
    paths.append(os.environ["HOME"]+"/agave-model/science-models/JSONFiles/")
    paths.append(os.environ["HOME"]+"/agave-model/machineFiles/")
    
    name_list = []
    package_list = []
    
    for p in paths:
        if os.path.isdir(p):      
            for filename in glob.glob(os.path.join(p, '*.json')):
                with open(os.path.join(os.getcwd(), filename), 'r') as f:
                    data = json.loads(f.read())          
                    name_list.append(data['name'])
                    package_list.append(data['package'] + '@' + data['version'])

            #if input_params.get("last_jid") != jetlag_conf.get_uv().jetlag_id:
            #    print("Done!")
    
    clean_name = []
    clean_package = []
    
    [clean_name.append(x) for x in name_list if x not in clean_name]
    [clean_package.append(x) for x in package_list if x not in clean_package]
    
    return tuple(clean_name), tuple(clean_package)
