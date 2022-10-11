import input_params
import logOp
from command import cmd
import re
import os
from jetlag_conf import get_uv
from write_env import write_env
import glob
import json
from paths import *
from here import here

def listdir_nohidden(path):
    return glob.glob(os.path.join(path, '*'))

def relink(dir_a, dir_b):
    for f in os.listdir(dir_a):
        fa = dir_a+"/"+f
        fb = dir_b+"/"+f
        if os.path.isdir(fa):
            os.makedirs(fb, exist_ok=True)
            relink(fa, fb)
        else:
            os.link(fa, fb)

def run(b):
    #d = input_params.get('middleware')
    m = input_params.get('last_jid')
    p = input_params.get('NPROCS')
    procs = []
    for pv in re.findall(r'\d+',p):
        procs += [int(pv)]
    while len(procs) < 3:
        procs += [1]
    t = input_params.get('title').lower()
    w = input_params.get('middleware')
    j = input_params.get('jobname')
    j = j.replace(' ', '_')
    
    logOp.log('run:',m,p,t,w)
    uv = get_uv()
    with logOp.logOp:
        cmd("rm -fr input.tgz run_dir",cwd=work_dir)
        cmd("mkdir -p run_dir",cwd=work_dir)
        write_env()
        #with open("run_dir/runapp.sh","w") as fd:
        #    print("singularity exec $SING_OPTS --pwd $PWD $IMAGE bash ./model-app.sh",file=fd)
        #cmd("cp model-app.sh run_dir/")
        
        for path in json_dirs:
            model_ver = input_params.get('modelversion_%s' % t)
            inputFileName = ""
            for filename in glob.glob(os.path.join(path, '%s-%s.json' %(t, model_ver))):
                with open(os.path.join(os.getcwd(), filename), 'r') as f:
                    data = json.loads(f.read())
                    inputFileName = data['inputFile']
        
        if not os.path.isdir(f"{model_dir}/input_{t}") or inputFileName not in listdir_nohidden(f"{model_dir}/input_{t}"):
            print("input_%s is empty. Using default files for model." % t)
            cmd(f"tar -xvf {model_dir}/input_{t}.tgz -C {work_dir}/")
        relink(f"{work_dir}/input_{t}", f"{work_dir}/run_dir")
        cmd("tar czvf input.tgz run_dir",cwd=work_dir)
        print("Procs:",procs,"=>",procs[0]*procs[1]*procs[2])
        with in_dir(work_dir):
            jobid = uv.run_job(j, nx=procs[0], ny=procs[1], nz=procs[2], jtype="queue", run_time="1:00:00", script_name="run-app")
