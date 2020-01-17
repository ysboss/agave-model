import input_params
import logOp
from command import cmd
import re
import os
from jetlag_conf import get_uv
from write_env import write_env

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
    d = input_params.get('middleware')
    m = input_params.get('machine_'+d)
    p = input_params.get('NPROCS')
    procs = []
    for pv in re.findall(r'\d+',p):
        procs += [int(pv)]
    while len(procs) < 3:
        procs += [1]
    t = input_params.get('title').lower()
    w = input_params.get('middleware')
    j = input_params.get('jobname')
    logOp.log('run:',m,p,t,w)
    uv = get_uv()
    with logOp.logOp:
        cmd("rm -fr input.tgz run_dir")
        cmd("mkdir -p run_dir")
        write_env()
        with open("run_dir/runapp.sh","w") as fd:
            print("singularity exec $SING_OPTS --pwd $PWD $IMAGE bash ./%s-app.sh" % t,file=fd)
        cmd("cp %s-app.sh run_dir/" % t)
        relink("input_%s" % t, "run_dir")
        cmd("tar czvf input.tgz run_dir")
        print("Procs:",procs,"=>",procs[0]*procs[1]*procs[2])
        jobid = uv.run_job(j, nx=procs[0], ny=procs[1], nz=procs[2], jtype="queue", run_time="1:00:00")
