from IPython.display import display
from ipywidgets import Output

logOp = Output()

def log(*arg,**karg):
    with logOp:
        print(*arg,**karg)

def clearLog():
    logOp.clear_output()
