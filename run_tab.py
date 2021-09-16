import input_params
import logOp
from command import cmd
import re
import os
from jetlag_conf import get_uv
from write_env import write_env
import glob
import json

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
        cmd("rm -fr input.tgz run_dir")
        cmd("mkdir -p run_dir")
        write_env()
        #with open("run_dir/runapp.sh","w") as fd:
        #    print("singularity exec $SING_OPTS --pwd $PWD $IMAGE bash ./model-app.sh",file=fd)
        #cmd("cp model-app.sh run_dir/")
        
        path = os.environ["HOME"]+"/agave-model/machineFiles/"
        model_ver = input_params.get('modelversion_%s' % t)
        inputFileName = ""
        for filename in glob.glob(os.path.join(path, '%s-%s.json' %(t, model_ver))):
            with open(os.path.join(os.getcwd(), filename), 'r') as f:
                data = json.loads(f.read())
                inputFileName = data['inputFile']
        
        if inputFileName not in listdir_nohidden("%s/agave-model/input_%s" % (os.environ["HOME"], t)) and not os.path.isdir("%s/agave-model/input_%s" % (os.environ["HOME"], t)):
            print("input_%s is empty. Using default files for model." % t)
            cmd("tar -xvf %s/agave-model/input_%s.tgz -C %s/agave-model/" % (os.environ["HOME"], t, os.environ["HOME"]))
        relink("input_%s" % t, "run_dir")
        # ERROR MESSAGE
        cmd("tar czvf input.tgz run_dir")
        print("Procs:",procs,"=>",procs[0]*procs[1]*procs[2])
        jobid = uv.run_job(j, nx=procs[0], ny=procs[1], nz=procs[2], jtype="queue", run_time="1:00:00", script_name="run-app")
#         jobid.wait()
#         try:
#             uv.get_file(jobid, "outputFiles.tgz",as_file="outputFiles.tgz")
#             cmd("rm -rf %s/agave-model/run_dir" % os.environ["HOME"])
#             cmd("tar -xvf %s/agave-model/outputFiles.tgz -C %s/agave-model/" % (os.environ["HOME"], os.environ["HOME"]))
#             cmd("rm %s/agave-model/outputFiles.tgz" % os.environ["HOME"])
#         except:
#             ###
#             print("Config failed: Is remote machine configured properly?")
#             print(job.err_output())
#             ###        
