import os
import re
from subprocess import Popen, STDOUT, PIPE
from shlex import split
from setvar import repvar

def cmd(arg,show=True,keep_endings=False):
    if type(arg) == str:
        pyargs = split(repvar(arg))
    else:
        pyargs = arg
    lines = []
    errs  = []
    print("cmd:"," ".join(pyargs))
    with Popen(pyargs,stderr=PIPE,stdout=PIPE) as pipe:
        for line in pipe.stdout.readlines():
            ld = line.decode()
            if not keep_endings:
                kld = re.sub(r'\s+$','',ld)
            else:
                kld = ld
            if show:
                print(ld,end='')
                os.write(1,line)
            lines += [kld]
        for line in pipe.stderr.readlines():
            ld = line.decode()
            if not keep_endings:
                kld = re.sub(r'\s+$','',ld)
            else:
                kld = ld
            if show:
                print(ld,end='')
                os.write(2,line)
            errs += [kld]
        rc = pipe.wait()
    return {'rc':rc,'stdout':lines,'stderr':errs}
