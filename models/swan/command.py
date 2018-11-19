import os
import re
from subprocess import Popen, STDOUT, PIPE
from shlex import split

def cmd(arg,show=True,keep_endings=False,inputs=""):
    if type(arg) == str:
        pyargs = split(arg)
    else:
        pyargs = [a for a in arg]
    lines = []
    errs  = []
    if show:
        print("cmd:"," ".join(pyargs))
    else:
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
