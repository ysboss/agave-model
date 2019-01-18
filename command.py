import os
import re
from subprocess import Popen, STDOUT, PIPE
from shlex import split
from setvar import repvar

def cmd(arg,show=True,keep_endings=False,inputs="",trace=True):
    if type(arg) == str:
        pyargs = split(repvar(arg))
    else:
        pyargs = [repvar(a) for a in arg]
    lines = []
    errs  = []
    if show:
        print("cmd:"," ".join(pyargs))
    elif trace:
        print("cmd:",pyargs[0],"...")
    with Popen(pyargs,stderr=PIPE,stdout=PIPE,stdin=PIPE,close_fds=True) as pipe:
        pipe.stdin.write(inputs.encode())
        pipe.stdin.close()
        for line in pipe.stdout.readlines():
            ld = line.decode()
            if not keep_endings:
                kld = re.sub(r'\s+$','',ld)
            else:
                kld = ld
            if show:
                print(ld,end='')
            lines += [kld]
        for line in pipe.stderr.readlines():
            ld = line.decode()
            if not keep_endings:
                kld = re.sub(r'\s+$','',ld)
            else:
                kld = ld
            if show:
                print(ld,end='')
            errs += [kld]
        rc = pipe.wait()
    return {'rc':rc,'stdout':lines,'stderr':errs}
