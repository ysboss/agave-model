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
    
def getModelsAndPacks():
    #print("Getting List of Models...")
    
    # Alternative Method
    # models = os.listdir("/home/jovyan/agave-model/models")
    # models = [x.upper() for x in models]
    
    path = os.environ["HOME"]+"/agave-model/JSON_Files/"
    name_list = []
    package_list = []
    ver_list = []
    for filename in glob.glob(os.path.join(path, '*.json')):
        with open(os.path.join(os.getcwd(), filename), 'r') as f:
            data = json.loads(f.read())          
            name_list.append(data['name'])
            package_list.append(data['package'] + '@' + data['version'])
    return tuple(name_list), tuple(package_list)
# Get list of all models we need to have in the CMR  

def packSplit(pack):
    temp = pack.split('@')
    return temp[0]
        
def get_versions(model):

    VERSIONS = []

    p = open("spack-info.txt").read()
    for g in re.finditer(r'(\w+)@([\d.]+)', p):
        package = g.group(1)
        version = g.group(2)

        if package == model.lower():
            VERSIONS.append(version)

    return VERSIONS
# Function to get the
# different versions of
# spack packages for
# a given model
          
    
def tarballHandler(tarName):
    mainPath = os.environ["HOME"]+"/agave-model"
    installedPath = mainPath+"/models"
    folderName = tarName.split('.t')
    # Split the tarball's name according to '.t' since all
    # tarball extensions begin with 't'
    # Ideally, the tarball will be named "model-version.tar/.tgz/.tar.gz"
    # JSON files should have a similar naming convention: model-version.json
    os.system("mkdir %s/%s" % (installedPath, folderName[0]))
    os.system("tar -xvf %s/models_to_install/%s -C %s/%s/" % (mainPath, tarName, installedPath, folderName[0]))
    os.system("mkdir %s/%s/tarball" % (installedPath, folderName[0]))
    os.system("mv %s/models_to_install/%s %s/%s/tarball/" % (mainPath, tarName, installedPath, folderName[0]))
    untar_path = installedPath+'/'+folderName[0]
    # Source code tar name should be determined when writing package.py file
    # Extracted files should be a tarball of the source code
    # for the model and a JSON file containing model details
    return untar_path
#Function to handle untar-ing user's tarballs


def cleanup(modelPath):
    os.system("rm %s/*.tar %s/*.tar.gz %s/*.tgz" % (modelPath, modelPath, modelPath))
    os.system("mv %s/tarball/* %s/tarball/.." % (modelPath, modelPath))
    os.system("rm -r %s/tarball" % modelPath)
# Removes the Source Code Tar and organizes the original file into the root of
# the respective model folder
    
    
def installNewModels():
    
    if os.path.isdir(os.environ["HOME"]+"/agave-model/models_to_install"):

        newModelsPath = os.environ["HOME"]+"/agave-model/models_to_install"
        
        if len(glob.glob(os.path.join(newModelsPath, '*'))) != 0:
            print("Looking for New Models to Build...")
            uv = jetlag_conf.get_uv()
            os.system("rm -fr input.tgz run_dir")
            os.system("mkdir -p run_dir")
            with HiddenPrint():
                write_env()
            
            spackPackList = []

            # Here, we make a list of all the models to be installed according
            # to their respective spack package
            for tarball in glob.glob(os.path.join(newModelsPath, '*')):
                if os.path.isfile(tarball):
                    os.system("cp %s %s/agave-model/run_dir/" % (tarball, os.environ["HOME"]))
                    modelSetupPath = tarballHandler(os.path.basename(tarball))
                    splitTarball = os.path.basename(tarball).split(".t")
                    with open("%s/%s.json" % (modelSetupPath, splitTarball[0].lower())) as f:
                        modelJSON = json.load(f)
                    print("New Model Found and Preparing to Install: %s (%s@%s)" % (modelJSON["name"], modelJSON["package"], modelJSON["version"]))
                    spackPackList.append(modelJSON["package"]+'@'+modelJSON["version"])
                    # Additionally, we move a copy of the tarball of the
                    # model's source code (in a tar also) to the run_dir so it can be placed
                    # on the server in the proper tarball directory (if needed)
                    os.system("mkdir -p %s/agave-model/JSON_Files" % os.environ["HOME"])
                    os.system("mv %s/*.json %s/agave-model/JSON_Files/" % (modelSetupPath, os.environ["HOME"]))
                    cleanup(modelSetupPath)

            print("Installing New Model(s). This may take awhile...")

            with HiddenPrint():

                with open("run_dir/tarballs.sh","w") as v:
                    print("#!/bin/bash", file=v)
                    print("mkdir -p /build-dir/tarballs/", file=v)
                    print("mkdir -p /build-dir/json", file=v)
                    print("tar -xvf *.tar -C /build-dir/tarballs/", file=v)
                    print("tar -xvf *.tgz -C /build-dir/tarballs/", file=v)
                    print("tar -xvf *.tar.gz -C /build-dir/tarballs/", file=v)
                    print("mv /build-dir/tarballs/*.json /build-dir/json/", file=v)                    
                os.system("chmod 755 run_dir/tarballs.sh")

                with open("run_dir/build-models.sh","w") as v:
                    print("#!/bin/bash", file=v)
                    #print("source /build-dir/ubuntu_xenial/spack/share/spack/setup-env.sh", file=v) # Need to make more generic
                    for pack in range(len(spackPackList)):
                        buildCommand = "spack install " + spackPackList[pack]
                        print(buildCommand, file=v)
                os.system("chmod 755 run_dir/build-models.sh")

                with open("run_dir/runapp.sh","w") as fd:
                    # For SUPER-MIKEII
                    #print("singularity exec $SING_OPTS --pwd $PWD $IMAGE bash ./tarballs.sh", file=fd)
                    #print("singularity exec $SING_OPTS --pwd $PWD $IMAGE bash ./build-models.sh", file=fd)
                    
                    #For QBC
                    print("singularity exec $SING_OPTS --pwd $PWD $IMAGE bash ./tarballs.sh", file=fd)
                    print("singularity exec $SING_OPTS --pwd $PWD $IMAGE bash ./build-models.sh", file=fd)
                    
                os.system("tar czvf input.tgz run_dir")
                jobid = uv.run_job("build-models", nx=4, ny=4, nz=1, jtype="queue", run_time="1:00:00")
                uv.wait_for_job(jobid)
            print("Done!")
            #gen_spack_pack_list()
        #else:
        #    print("No New Models Found!")
    else:
        os.system("mkdir %s/agave-model/models_to_install" % os.environ["HOME"])
        print("Models can now be installed in \"models_to_install\"")   

              
              
def gen_spack_pack_list():
    uv = jetlag_conf.get_uv()
    os.system("rm -fr input.tgz run_dir")
    os.system("mkdir -p run_dir")
    print("Retrieving Model Versions List...")
    print("This may take a few minutes")
    with HiddenPrint():
        write_env()
        with open("run_dir/get-versions.sh","w") as v:
            print("#!/bin/bash", file=v)
            print("source /build-dir/ubuntu_xenial/spack/share/spack/setup-env.sh", file=v)
            print("spack find > spack-info.txt", file=v)
        os.system("chmod 755 run_dir/get-versions.sh")
        with open("run_dir/runapp.sh","w") as fd:
            print("singularity exec $SING_OPTS --pwd $PWD $IMAGE bash ./get-versions.sh", file=fd)
        os.system("tar czvf input.tgz run_dir")
        jobid = uv.run_job("get_model_versions", nx=4, ny=4, nz=1, jtype="queue", run_time="1:00:00")
        uv.wait_for_job(jobid)
        uv.get_file(jobid, "run_dir/spack-info.txt",as_file="spack-info.txt")
    print("Done!\n\n")
    