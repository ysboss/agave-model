from setvar import *
import os

def cmd(cmd):
    cmd = repvar(cmd)
    print("cmd=",cmd)
    os.system(cmd+" 2>&1")
