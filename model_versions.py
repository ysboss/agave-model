from jetlag import RemoteJobWatcher
from subprocess import Popen, PIPE
import re
from command import cmd
from write_env import write_env
import jetlag_conf
import os, sys
        
# Function to get the
# different versions of
# spack packages for
# a given model

def get_versions(model):

    VERSIONS = []

    p = open("spack-info.txt").read()
    for g in re.finditer(r'(\w+)@([\d.]+)', p):
        package = g.group(1)
        version = g.group(2)

        if package == model:
            VERSIONS.append(version)

    return VERSIONS

def gen_spack_pack_list():
    uv = jetlag_conf.get_uv()
    os.system("rm -fr input.tgz run_dir")
    os.system("mkdir -p run_dir")
    with open("spack-log.txt", "w") as f:
        default_stdout = sys.stdout
        sys.stdout = f
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
        sys.stdout = default_stdout
    