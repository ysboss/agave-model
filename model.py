from __future__ import print_function
import os, re
import numpy as np
import ipywidgets
from ipywidgets import interactive, Layout, Button, Box, HBox, VBox, Text, Dropdown, Label, IntSlider, Textarea, Accordion, ToggleButton, ToggleButtons, Select, HTMLMath, FloatRangeSlider, Output, Tab, Checkbox, HTML
from IPython.display import display, clear_output, HTML
import json
import traceback
import sys

from agave import *
from setvar import *
from fwPlots import *
from swanPlots import *
from command import cmd
from modInput import modInput

import imp
if "jetlag" in globals():
    imp.reload(jetlag)
else:
    import jetlag
from jetlag import *
from knownsystems import *

######################## Previous ############################################################

def bread(fname):
    fd = os.open(fname,os.O_RDONLY)
    s = ''
    while True:
        contents = os.read(fd,1000)
        if len(contents) == 0:
            break
        for k in contents:
            s += chr(k)
    os.close(fd)
    return re.findall(r'.*\n?',s)

tab_nest = None

def relink(dir_a, dir_b):
    for f in os.listdir(dir_a):
        fa = dir_a+"/"+f
        fb = dir_b+"/"+f
        if os.path.isdir(fa):
            os.makedirs(fb, exist_ok=True)
            relink(fa, fb)
        else:
            os.link(fa, fb)

uv = Universal()
uv.load(
    backend_agave,
    'sbrandt@cct.lsu.edu',
    'shelob'
)
uv.refresh_token()

cur_model = 'swan'
logOp = Output()
logStash = Output()   # use to receive logs that are stashed for user
clearLogBtn = Button(description='Clear log', button_style='primary', layout = Layout(width = '115px'))

modelTitle = Dropdown(options=['SWAN', 'Funwave_tvd','Delft3D', 'OpenFoam', 'Cactus', 'NHWAVE'])
modelVersion = Dropdown()
modelBox = VBox([Box([Label(value="Model", layout = Layout(width = '50px')), modelTitle]), 
                 Box([Label(value="Version", layout = Layout(width = '50px')),modelVersion])])
globalBox = Box([modelBox, clearLogBtn], 
               layout = Layout(display = 'flex', flex_flow = 'row', justify_content = 'space-between', width = '100%'))

def clearLog_btn_clicked(a):
    logOp.clear_output()
    msgOut.clear_output()

clearLogBtn.on_click(clearLog_btn_clicked)

def generatePara(templateFile):
    items = []
    if True: #with open(templateFile, 'r') as fd:
        for line in bread(templateFile): #fd.readlines():
            g = re.search(r'[\w:]*\s*.*=*\s*\${(.*)}',line)
            if g:
                label_value = ''
                isTB = False
                for match in re.findall(r'(\w+)=("[^"]*"|\'[^\']*\'|[^,\n]*)', g.group(1)):
                    if match[0] == 'label':
                        if match[1][0] == '"' and match[1][-1] == '"':
                            val = match[1][1:-1]
                        elif match[1][0] == "'" and match[1][-1] == "'":
                            val = match[1][1:-1]
                        else:
                            val = match[1]
                        lbs = val.split('/')
                        label_value = lbs[0]
                        if len(lbs) == 2:
                            isTB = True
                    if match[0] == 'option':
                        ops = match[1].split('/')
                        # if the first element of options is 'CO', remove it's label name.
                        if ops[0] == 'CO':
                            label = Label(layout = Layout(width = "150px"))
                            if not isTB:
                                togBtns = ToggleButtons(options = ops[1:])
                            else:
                                togBtns = ToggleButton(description = ops[1], value = True)
                        else:
                            label = Label(value = label_value, layout = Layout(width = "150px"))
                            if not isTB:
                                togBtns = ToggleButtons(options = ops)
                            else:
                                togBtns = ToggleButton(description = ops[0], value = True)
                        box = Box([label, togBtns], layout = Layout(width = '100%', justify_content = 'flex-start'))
                        items.append(box)
                    if match[0] == 'value':
                        label = Label(value = label_value, layout = Layout(width = "150px"))
                        text = Text(value = match[1])
                        box = Box([label, text], layout = Layout(width = '100%', justify_content = 'flex-start'))
                        items.append(box)
    return items

def updatePara(templateFile, newInput, inputBox):
    with open(newInput, "w") as fw:
        if True: #with open(templateFile, "r") as fd:
            count = 0
            for line in bread(templateFile): #fd.readlines():
                g = re.search(r'[\w:]*\s*.*=*\s*\${(.*)}' , line)
                if g:
                    isTB = False
                    isStr = False
                    string = ''
                    newVals = []
                    for match in re.findall(r'(\w+)=("[^"]*"|\'[^\']*|[^,\n]*)', g.group(1)):
                        if match[0] == 'label':
                            lbs = match[1].split('/')
                            if (len(lbs) == 2):
                                isTB = True
                        if match[0] == 'string':
                            string = match[1]
                            isStr = True
                        if match[0] == 'option':
                            if not isTB:
                                if isStr:
                                    if inputBox.children[count].children[1].value == 'True':
                                        newVals.append(string[1:-1])
                                else:
                                    newVals.append(inputBox.children[count].children[1].value)
                            else:
                                if (inputBox.children[count].children[1].value):
                                    newVals.append(inputBox.children[count].children[1].description)
                            count+=1
                        if match[0] == 'value':
                            newVals.append(inputBox.children[count].children[1].value)
                            count+=1
                    newLine = ''
                    for item in newVals:
                        newLine = newLine + ' ' + item + ' '
                    fw.write(re.sub(r'\${.*}', newLine, line))
                else:
                    fw.write(line)
        #fd.close()
    #fw.close()    
    

menus = {}
def set_tabs():
        global cur_model, menus
        tabs = ["Choose Input Template"]
        menus[cur_model] = {}
        for f in os.listdir("input_"+cur_model):
            if not re.search(r'_template',f):
                continue
            fn = "input_"+cur_model+"/"+f
            #with open(fn,"r") as fr:
            if True:
                found = False
                for line in bread(fn): #fr.readlines():
                    g = re.search(r'\bmenu:\s*(.*\S)\s*->\s*(.*\S)',line)
                    if g:
                        label = g.group(1)
                        menus[cur_model][label] = {}
                        menus[cur_model][label]["outfile"] = g.group(2)
                        menus[cur_model][label]["infile"] = f
                        found = True
            if not found:
                label = f
                menus[cur_model][label] = {}
                menus[cur_model][label]["outfile"] = re.sub(r'_template','',f)
                menus[cur_model][label]["infile"] = f
            tabs += [label]
        if tab_nest is not None:
            item = tab_nest.children[0].children[0]
            tabs = tuple(tabs)
            if item.options == tabs:
                return tabs
            item.options = tabs
            item.index = 0
        return tabs
    
def template_on_change(change):
    set_tabs()
    inputTmp = ''
    if change['type'] == 'change' and change['name'] == 'value':
#        if(change['new'] == 'Choose Input Template'):
#            #tab_nest.children[0].children[2].children = []
#            return
#        if(change['new'] == 'Basic Template'):
#            with logOp:
#                cmd("tar -xvf input_" + cur_model + ".tgz")
#            inputTmp = 'input_' + cur_model + '/basic_template.txt'
#        if(change['new'] == 'HDF5 Template'):
#            with logOp:
#                cmd("tar -xvf input_" + cur_model + ".tgz")
#            inputTmp = 'input_' + cur_model + '/hdf5_template.txt'
#        
         item = tab_nest.children[0].children[0]
         if item.index is not None:
            val = item.options[item.index]
            if val not in menus[cur_model]:
                return
            inputTmp = 'input_' + cur_model + '/' + menus[cur_model][val]["infile"]
            tab_nest.children[0].children[2].children = generatePara(inputTmp)
        
        
def update_btn_clicked(a):
    set_tabs()
    item = tab_nest.children[0].children[0]
    itemValue = item.options[item.index]
    if itemValue not in +menus[cur_model]:
        return
    inputFile = "input_"+cur_model+"/"+menus[cur_model][itemValue]["infile"]
    outputFile = "input_"+cur_model+"/"+menus[cur_model][itemValue]["outfile"]
    updatePara(inputFile, outputFile, tab_nest.children[0].children[2])
#    if (tab_nest.children[0].children[1].value == True):
#        with logOp:
#            cmd("rm -f input.tgz")
#            cmd("rm -fr input")
#            cmd("cp -f ../input_" + cur_model + ".tgz input.tgz")
#            return
#        
#    newInput = 'input_'+ cur_model + '/input_tmp.txt'
#    inputTmp = ''
#    if(tab_nest.children[0].children[0].value == 'Basic Template'):
#        inputTmp = 'input_' + cur_model + '/basic_template.txt'
#    if(tab_nest.children[0].children[0].value == 'HDF5 Template'):
#        inputTmp = 'input_' + cur_model + '/basic_template.txt'
#    
#    updatePara(inputTmp, newInput, tab_nest.children[0].children[2])
#    
#    tab_nest.children[0].children[4].value = open(newInput, 'r').read()
  
             
    



######################## Previous end ############################################################

######################## SWAN Input tab ############################################################

swanInputdd = Dropdown(options=set_tabs(), value='Choose Input Template')
swanCbox = Checkbox(value = False, description = "Use Own Input")
swanInput = Box(layout = Layout(flex_flow = 'column'))
swanInputdd.observe(template_on_change)
swanUpInputBtn = Button(description='Update Input File',button_style='primary', layout=Layout(width='100%'))
swanUpInputBtn.on_click(update_btn_clicked)
swanInputArea = Textarea(layout= Layout(height = "300px",width = '100%'))
swanInputBox = Box([swanInputdd, swanCbox, swanInput, swanUpInputBtn, swanInputArea], 
                 layout = Layout(flex_flow = 'column', align_items = 'center'))

######################## SWAN Input tab end############################################################



##################################### Funwave-tvd Input tab ################################


fwInputdd=Dropdown(options=['Choose Input Template','Basic Template'], value='Choose Input Template')
fwCbox = Checkbox(value = False, description = "Use Own Input")
fwInput = Box(layout = Layout(flex_flow = 'column'))    
fwInputdd.observe(template_on_change)
fwUpInputBtn = Button(description='Update Input File',button_style='primary', layout=Layout(width='100%'))
fwUpInputBtn.on_click(update_btn_clicked)
fwInputArea = Textarea(layout= Layout(height = "300px",width = '100%'))
fwInputBox = Box([fwInputdd, fwCbox, fwInput, fwUpInputBtn, fwInputArea], 
                  layout = Layout(flex_flow = 'column', align_items = 'center'))

##################################### Funwave-tvd Input tab end ###############################

##################################### Cactus Input tab ################################


cacInputdd=Dropdown(options=['Choose Input Template','Basic Template','HDF5 Template'], value='Choose Input Template')
cacCbox = Checkbox(value = False, description = "Use Own Input")
cacInput = Box(layout = Layout(flex_flow = 'column'))    
cacInputdd.observe(template_on_change)     
cacUpInputBtn = Button(description='Update Cactus Input File',button_style='primary', layout=Layout(width='100%'))
cacUpInputBtn.on_click(update_btn_clicked)
cacInputArea = Textarea(layout= Layout(height = "300px",width = '100%'))
cacInputBox = Box([cacInputdd, cacCbox, cacInput, cacUpInputBtn, cacInputArea], 
                  layout = Layout(flex_flow = 'column', align_items = 'center'))

##################################### Cactus Input tab end ###############################



##################################### NHWAVE Input tab ################################


nhInputdd=Dropdown(options=['Choose Input Template','Basic Template'], value='Choose Input Template')
nhCbox = Checkbox(value = False, description = "Use Own Input")
nhInput = Box(layout = Layout(flex_flow = 'column'))    
nhInputdd.observe(template_on_change)
nhUpInputBtn = Button(description='Update Input File',button_style='primary', layout=Layout(width='100%'))
nhUpInputBtn.on_click(update_btn_clicked)
nhInputArea = Textarea(layout= Layout(height = "300px",width = '100%'))
nhInputBox = Box([nhInputdd, nhCbox, nhInput, nhUpInputBtn, nhInputArea], 
                  layout = Layout(flex_flow = 'column', align_items = 'center'))

##################################### Funwave-tvd Input tab end ###############################





##################################### Delft3D Input tab ######################################

delft3d_items=[Label(value='Coming soon', layout = Layout(width = '200px'))]   
delft3dBox = Box(delft3d_items, layout= Layout(flex_flow = 'column', align_items='stretch', disabled=False))

##################################### Delft3D Input tab end ###############################






##################################### OpenFoam Input tab ######################################

ofCaseName = Dropdown()
ofOwnCaseName = Dropdown(options=["Select Input Case of Own"])
ofCbox = Checkbox(value = False, description = "Use Own Input")
casesTutorials = ["Select Input Case of Tutorials"]
casesOwn = ["Select Input Case of Own"]

with logStash:
    cmd("tar -xvf input_openfoam.tgz")
    with open("input_openfoam/tutorials/cases.txt", 'r') as fr:
        lines = fr.readlines()
        for line in lines:
            casesTutorials.append(line)
        ofCaseName.options = casesTutorials 
        
def ofCbox_change(change):
    if change['type'] == 'change' and change['name'] == 'value':
        if(change['new'] == True):
            ownfiles = os.listdir("input_openfoam/foam_run/")
            ofOwnCaseName.options = ownfiles
        if(change['new'] == False):
            ofOwnCaseName.options = ["Select Input Case of Own"]
            
ofCbox.observe(ofCbox_change)
            
def ofUpInput_btn_clicked(a):
    if (ofCbox.value == True):
        with logOp:
            cmd("rm -f input.tgz")
            cmd("rm -fr input")
            cmd("cp -f input_openfoam/foam_run/" + ofOwnCaseName.value + " input.tgz")
            return
        
    if not ofCaseName.value == "Select Input Case":
        with open("input_openfoam/tutorials/" + ofCaseName.value[:-1] + "/system/decomposeParDict", "r") as fd:
            contents = fd.read()
            ofInputArea.value = contents
            sp = r'(?:\s|//.*)'
            pat = re.sub(r'\\s',sp,r'coeffs\s*{\s*n\s+\(\s*(\d+)\s+(\d+)\s+(\d+)\s*\)\s*;\s*}')
            g = re.search(pat, contents)
            if g:
                numXSlider.value = g.group(1)
                numYSlider.value = g.group(2)
                numZSlider.value = g.group(3)
        fd.close()

ofUpInputBtn = Button(description='Update OpenFoam Input File',button_style='primary', layout=Layout(width='100%'))
ofUpInputBtn.on_click(ofUpInput_btn_clicked)

ofInputArea = Textarea(layout= Layout(height = "300px",width = '100%'))
   
ofInputBox = Box([ofCaseName, ofCbox, ofOwnCaseName, ofUpInputBtn, ofInputArea], 
                 layout = Layout(flex_flow = 'column', align_items = 'center'))

##################################### OpenFoam Input tab end ###############################




##################################### Run tab #################################################
run_item_layout = Layout(
    display = 'flex',
    flex_flow = 'row',
    justify_content = 'flex-start',
    width = '50%'
)

jobNameText = Text(value = 'myjob')

machines = Dropdown()
queues = Dropdown()

machines_options = []
all_apps = {}
exec_to_app = {}

for m in uv.get_meta('system-config-*'):
    val = m["value"]

    uv2 = Universal()
    uv2.init(
        backend=uv.values["backend"],
        email=uv.values["email"],
        **val)

    perm_data_str = ''
    pems_data = uv2.get_app_pems()
    if 'read' in pems_data and pems_data['read'] == True:
        perm_data_str += 'R'
    if 'write' in pems_data and pems_data['write'] == True:
        perm_data_str += 'W'
    if 'execute' in pems_data and pems_data['execute'] == True:
        perm_data_str += 'X'

    machine = uv2.values["execm_id"]

    machines_options += [machine]

    app_entry = {
        'exec_sys' : machine,
        'storage_sys' : uv2.values["storage_id"],
        'perm' : perm_data_str,
        'queues' : [
            { "name": val["queue"],
              "ppn" : val["max_procs_per_node"] }
        ],
        'uv':uv2
    }
    app0 = uv2.fill(uv2.values["app_name"]+"-"+uv2.values["app_version"])
    all_apps[app0] = app_entry
    exec_to_app[machine] = app0

machines.options = machines_options

#queues.options = queues_options

def on_machine_value_set(_):
    queues_options = []
    exec_sys = machines.value
    app0 = exec_to_app[exec_sys]
    for q in range(len(all_apps[app0]["queues"])):
        queues_options += [all_apps[app0]["queues"][q]["name"]]
    queues.options = queues_options
    queues.value = queues_options[0]

machines.observe(on_machine_value_set)
exec_sys = all_apps[app0]["exec_sys"]
machines.value = exec_sys
on_machine_value_set(None)

def get_uv():
    app = exec_to_app[exec_sys]
    app_data = all_apps[app]
    return app_data["uv"]

numXSlider = IntSlider(value=0, min=1, max=16, step=1)
numYSlider = IntSlider(value=0, min=1, max=16, step=1)
numZSlider = IntSlider(value=0, min=1, max=16, step=1)

runBtn = Button(description='Run', button_style='primary', layout= Layout(width = '50px'))

run_items = [
    Box([Label(value="Job Name", layout = Layout(width = '350px')), jobNameText], layout = run_item_layout),
    Box([Label(value="Machine", layout = Layout(width = '350px')), machines], layout = run_item_layout),
    Box([Label(value="Queue", layout = Layout(width = '350px')), queues], layout = run_item_layout),
    Box([Label(value="NX", layout = Layout(width = '350px')), numXSlider], layout = run_item_layout),
    Box([Label(value="NY", layout=Layout(width = '350px')), numYSlider], layout= run_item_layout),
    Box([Label(value="NZ", layout=Layout(width = '350px')), numZSlider], layout= run_item_layout),
    Box([runBtn]),
]

def modify_openfoam(case):
    with logOp:
        print("openfoam:",case)
    sp = case.split('/')
    caseName = sp[len(sp)-1].strip()
    tmp = ""
    with open("run_dir/tutorials/%s/system/decomposeParDict" % case.strip(), "r") as fd:
        contents = fd.read()
        procs = get_procs()
        pat1 = r'numberOfSubdomains\s+(\d+)\s*;'
        pat2 = r'coeffs\n\s*{\n\s*n\s*\(\s*(\d+)\s+(\d+)\s+(\d+)\s*\);\s*\n}'
        c = re.sub(pat1, 'numberOfSubdomains %d;\n' %(procs[0]), contents)
        d = re.sub(pat2, 'coeffs\n{\n   n   (%d %d %d);\n}\n' %(procs[1], procs[2], procs[3]), c)
        tmp = d
        fd.close()
    with open("input/system/decomposeParDict", "w") as fd:
        for line in tmp:
            fd.write(line)
        fd.close()

def get_procs():
    nx = numXSlider.value
    ny = numYSlider.value
    nz = numZSlider.value
    return (nx*ny*nz,nx,ny,nz)

def runfun_btn_clicked(a):
    exec_sys = machines.value
    app = exec_to_app[exec_sys]
    app_data = all_apps[app]
    queue = queues.value
    with logOp:
        setvar("APP_NAME=%s" % app)
        setvar("STORAGE_MACHINE=%s" % app_data["storage_sys"])
        setvar("EXEC_MACHINE=%s" % exec_sys)
        setvar("QUEUE=%s" % queue)
    ppn = 1
    for i in range(len(app_data["queues"])):
        if app_data["queues"][i]["name"] == queue:
            ppn = int(app_data["queues"][i]["ppn"])
    procs = get_procs()

    nodes = procs[0]//ppn
    if procs[0] % ppn != 0:
        nodes += 1
        
    with logOp:
        if (tab_nest.children[0].children[1].value == False):
            cmd("rm -fr run_dir") 
            cmd("mkdir run_dir")
            in_dir = "input_" + cur_model
            for fn in os.listdir(in_dir):
                cmd("cp -a '%s/%s' ./run_dir/" % (in_dir,fn))
            if (cur_model == "openfoam"):
                modify_openfoam(ofCaseName.value)
                
            cmd("tar cvzf input.tgz run_dir")
                
        setvar("INPUT_DIR=${AGAVE_USERNAME}_$(date +%Y-%m-%d_%H-%M-%S)")
        #cmd("files-mkdir -S ${STORAGE_MACHINE} -N inputs/${INPUT_DIR}")
        #cmd("files-upload -F input.tgz -S ${STORAGE_MACHINE} inputs/${INPUT_DIR}/")
        #cmd("files-mkdir agave://${STORAGE_MACHINE}/inputs/${INPUT_DIR}")
        #cmd("files-cp input.tgz agave://${STORAGE_MACHINE}/inputs/${INPUT_DIR}/")
        #submitJob(nodes, procs[0], cur_model, jobNameText.value, machines.value, queues.value)
        uv = app_data["uv"]
        ###
        jetlag_app = cur_model
        call(["rm", "-fr", "run_dir"])
        os.makedirs('run_dir')
        with open("run_dir/runapp.sh","w") as fd:
            print("singularity exec $SING_OPTS --pwd $PWD $IMAGE bash ./%s-app.sh" % jetlag_app,file=fd)
            #print("bash ./%s-app.sh" % jetlag_app)
        call(["cp", "%s-app.sh" % jetlag_app, "run_dir/."])
        #for fname in os.listdir("input_%s" % jetlag_app):
        #    call(["ln","input_%s/%s" % (jetlag_app, fname),"run_dir/"])
        relink("input_%s" % jetlag_app, "run_dir")
        call(["tar", "czf", "input.tgz", "run_dir"])
        ###
        nx = numXSlider.value
        ny = numYSlider.value
        nz = numZSlider.value
        uv.run_job(jobNameText.value, nx=nx, ny=ny, nz=nz, jtype="queue", run_time="1:00:00")
        
runBtn.on_click(runfun_btn_clicked)

runBox = VBox(run_items)

##################################### Run tab end #################################################



################################# Output tab ###################################

jobListBtn = Button(description='List all jobs', button_style='primary', layout= Layout(width = '115px'))

jobSelect = Select(layout = Layout(height = '150px', width='100%'))

jobOutputBtn = Button(description='List job output', button_style='primary', layout= Layout(width = '115px'))

abortBtn = Button(description='Abort', button_style='danger', layout= Layout(width = 'auto'))

outputSelect = Select(layout = Layout(height = '150px', width='100%'))

downloadOpBtn = Button(description='Download', button_style='primary', layout= Layout(width = '115px'))

jobHisBtn = Button(description='Job history', button_style='primary', layout= Layout(width = '115px'))

jobHisSelect = Select(layout = Layout(height = '336px', width='100%'))

def jobList_btn_clicked(a):
    with logOp:
        out1 = []
        uv = get_uv()
        for j in uv.job_list(10):
            out1 += [j["id"]+" "+j["status"]]
        jobSelect.options = out1
    
jobListBtn.on_click(jobList_btn_clicked)

def abort_btn_clicked(a):
    g = re.match(r'^\S+',jobSelect.value)
    with logOp:
        if g:
            jobid = g.group(0)
            rcmd = "jobs-stop "+jobid
            cmd(rcmd)

abortBtn.on_click(abort_btn_clicked)


def jobOutput_btn_clicked(a):
    g = re.match(r'^\S+',jobSelect.value)
    with logOp:
        if g:
            jobid = g.group(0)
            #rcmd = "jobs-output-list "+ jobid
            #cout = cmd(rcmd)
            #out1 = cout["stdout"]
            uv = get_uv()
            outputSelect.options = ["loading..."]
            out1 = uv.show_job(jobid,verbose=False)
            outputSelect.options = out1
            if len(out1)==0:
                outputSelect.options = ["empty"]
        else:
            print("pattern did not match:",jobSelect.value)
    
jobOutputBtn.on_click(jobOutput_btn_clicked)

def download_btn_clicked(a):
    with logOp:
        try:
            g = re.match(r'^\S+',jobSelect.value)
            jobid = g.group(0)
            uv = get_uv()
            #if(outputSelect.value.find('.')==-1):
            #    rcmd = "jobs-output-get -r "+ jobid +" "+ outputSelect.value
            #else:
            #    rcmd = "jobs-output-get "+ jobid +" "+ outputSelect.value

        
            if outputSelect.value == '/output.tgz':
                with logOp:
                    print("Downloading output tarball to jobdata-"+jobid)
                job = RemoteJobWatcher(uv, jobid)
                job.get_result()
            elif re.match(r'.*\.(txt|out|err|ipcexe)',outputSelect.value):
                rcmd = uv.get_file(jobid,outputSelect.value)
                print(decode_bytes(rcmd))
            else:
                with logOp:
                    print("Download:",outputSelect.value)
                rcmd = uv.get_file(jobid,outputSelect.value)
        except Exception as ex:
            with logOp:
                print("DIED!",ex)
                traceback.print_exc(file=sys.stdout)

downloadOpBtn.on_click(download_btn_clicked)

def jobHis_btn_clicked(a):
    g = re.match(r'^\S+', jobSelect.value)
    with logOp:
        if g:
            jobid = g.group(0)
            #rcmd = "jobs-history -V " + jobid
            #cout = cmd(rcmd)
            #out1 = cout["stdout"]
            uv = get_uv()
            hist = uv.job_history(jobid)
            out1 = []
            for item in hist:
                out1 += [
                    item["status"]+" "+
                    item["created"]+"\n"+
                    item["description"]
                ]
            jobHisSelect.options = out1
    
jobHisBtn.on_click(jobHis_btn_clicked)


output_items_left = [
    Box([jobListBtn]),
    Box([jobSelect], layout = Layout(width='100%')),
    Box([jobOutputBtn,abortBtn], layout = Layout(display = 'flex', justify_content = 'space-between', width='100%')),
    Box([outputSelect], layout = Layout(width='100%')),
    Box([downloadOpBtn])
]

output_items_right = [
    Box([jobHisBtn]),
    Box([jobHisSelect],layout = Layout(width='100%'))
]

outputBox = HBox([VBox(output_items_left, layout = Layout(width='50%')), VBox(output_items_right, layout = Layout(width='50%'))],
                layout = Layout(width='100%'))

#outputBox = HBox(output_items_right)

################################# Output tab end ###################################


################################# building tab  ###################################
build_item_layout = Layout(
    display = 'flex',
    flex_flow = 'row',
    justify_content = 'flex-start',
    width = '50%'
)

modelDd = Dropdown(options=['Swan','Funwave_tvd','OpenFoam', 'NHWAVE'])
modelVersionDd = Dropdown(options = ['4120','4110AB'])
mpiDd = Dropdown(options = ['None','3.3','3.2', '3.1.4'])
h5Dd = Dropdown(options = ['None','1.10.5','1.10.4', '1.8.21'])
hypreDd = Dropdown(options = ['None','2.11.2', '2.10.1'])

buildBtn = Button(description = "Build", button_style='primary', layout= Layout(width = '50px'))
build_model = Label(value=modelTitle.value + " VERSION", layout = Layout(width = '350px'))
msgOut = Output()

build_items = [
    Box([build_model, modelVersionDd], layout = build_item_layout),
    Box([Label(value="Build Machine", layout = Layout(width = '350px')), machines], layout = build_item_layout),
    Box([Label(value="Queue", layout = Layout(width = '350px')), queues], layout = build_item_layout),
    ipywidgets.HTML(value="<b><font color='OrangeRed'><font size='2.5'>Select Dependent Software</b>"), 
    #Box([Label(value="MODEL", layout = Layout(width = '350px')), modelDd], layout = build_item_layout),
    Box([Label(value="MPICH", layout = Layout(width = '350px')), mpiDd], layout = build_item_layout),
    Box([Label(value="HDF5", layout = Layout(width = '350px')), h5Dd], layout = build_item_layout),
    Box([Label(value="HYPRE", layout = Layout(width = '350px')), hypreDd], layout = build_item_layout),
    Box([buildBtn]),
    Box([msgOut])
]

# def model_change(change):
#     if change['type'] == 'change' and change['name'] == 'value':
#         if(change['new'] == 'Swan'):
#             modelVersionDd.options = ['41.20','40.85']
#         if(change['new'] == 'Funwave-tvd'):
#             modelVersionDd.options = ['3.3','3.2', '3.1', '3.0']
#         if(change['new'] == 'OpenFoam'):
#             modelVersionDd.options = ['1812','1806', '1712']
#         if(change['new'] == 'NHWAVE'):
#             modelVersionDd.options = ['3.0']
def isjobexist():
    query_terms = 'model='+modelTitle.value+'&model_ver='+modelVersionDd.value+'&mpich='+mpiDd.value+'&hdf5='+h5Dd.value+'&hypre='+hypreDd.value
    query_cmd = "jobs-search 'status=FINISHED' 'parameters.like={*\"versions\":\""+query_terms+"\"*}'"
    with logOp:
        print (query_cmd)
    
    out = cmd(query_cmd,show=False,trace=False)
    result = out['stdout'][0]
    if not result:
        return False
    return True
        
         
def buildBtn_clicked(a):
    model_ver = modelTitle.value.upper() + "_VER"
    mpi_ver = '' if mpiDd.value is "None" else mpiDd.value
    h5_ver = '' if h5Dd.value is "None" else h5Dd.value
    hypre_ver = '' if hypreDd.value is "None" else hypreDd.value
    
    with logOp:
        setvar("MPICH_VER=" + mpiDd.value)
        setvar("HDF5_VER=" + h5Dd.value)
        setvar("HYPRE_VER=" + hypreDd.value)
        setvar("MODEL_VER=" + modelVersionDd.value)
        writefile("env_setting.txt","""
#!/bin/bash
export """+model_ver+"""="""+modelVersionDd.value+"""
export MPICH_VER="""+mpi_ver+"""
export H5_VER="""+h5_ver+"""
export HYPRE_VER="""+hypre_ver+"""
    """)
    
#     cmd("rm -fr build_input") 
#     cmd("mkdir build_input")
#     cmd("cp env_setting build_input/")
        exist = isjobexist()
        if exist is True:
            with msgOut:
                print ("The job exist, no build job would be submitted!")
        else:
            setvar("INPUT_DIR=${AGAVE_USERNAME}_$(date +%Y-%m-%d_%H-%M-%S)")
            cmd("files-mkdir -S ${STORAGE_MACHINE} -N inputs/${INPUT_DIR}")
            cmd("files-upload -F env_setting.txt -S ${STORAGE_MACHINE} inputs/${INPUT_DIR}/")
            submitBuildJob(machines.value, queues.value)
            
            # set job permissions to users
            #users = ['ysboss','tg457049','lzhu','nanw','reza']
            #for user in users:
            #    cmd('jobs-pems-update -u '+user+' -p READ ${JOB_ID}')
            
    
buildBtn.on_click(buildBtn_clicked)
            
#modelDd.observe(model_change)

buildTab = VBox(build_items)


################################# image tab end ###################################



################################ Finally ##########################################################
        
tab_nest = Tab()
tab_nest.children = [swanInputBox, runBox, outputBox, buildTab]
tab_nest.set_title(0, 'Input')
tab_nest.set_title(1, 'Run')
tab_nest.set_title(2, 'Output')
tab_nest.set_title(3, 'Build')

#uv.refresh_token()
clear_output()

def on_change(change):
    global cur_model
    if change['type'] == 'change' and change['name'] == 'value':
        with logOp:
            setvar("MODEL_TITLE="+modelTitle.value)
        cur_model = modelTitle.value.lower()
    
        build_model.value = modelTitle.value + " VERSION"
        set_tabs()

#        if(change['new'] == 'SWAN'):
#            modelVersionDd.options = ['4120','4110AB']
#            cur_model = 'swan'
#            out.clear_output()
#            with out:
#                tab_nest.children = [swanInputBox, runBox, outputBox, buildTab]
#                display(tab_nest)
#                
#        if(change['new'] == 'Funwave_tvd'):
#            modelVersionDd.options = ['3.3']
#            cur_model = 'funwave'
#            out.clear_output()
#            with out:
#                tab_nest.children = [fwInputBox, runBox, outputBox, buildTab]
#                display(tab_nest)
#        if(change['new'] == 'Cactus'):
#            modelVersionDd.options = []
#            cur_model = 'cactus'
#            out.clear_output()
#            with out:
#                tab_nest.children = [cacInputBox, runBox, outputBox, buildTab]
#                display(tab_nest)
#        if(change['new'] == 'Delft3D'):
#            modelVersionDd.options = []
#            cur_model = 'delft3d'
#            out.clear_output()
#            with out:
#                tab_nest.children = [delft3dBox, runBox, outputBox, buildTab]
#                display(tab_nest)
#        if(change['new'] == 'OpenFoam'):
#            modelVersionDd.options = ['1812','1806', '1712']
#            cur_model = 'openfoam'
#            out.clear_output()
#            with out:
#                tab_nest.children = [ofInputBox, runBox, outputBox, buildTab]
#                display(tab_nest)
#        if(change['new'] == 'NHWAVE'):
#            modelVersionDd.options = ['3.0']
#            cur_model = 'nhwave'
#            out.clear_output()
#            with out:
#                tab_nest.children = [nhInputBox, runBox, outputBox, buildTab]
#                display(tab_nest)
                
modelTitle.observe(on_change)

display(globalBox)

out = Output()

with out:
    display(tab_nest)
    
display(out)

display(logOp)

if "MODEL_TITLE" in os.environ:
    modelTitle.value = os.environ["MODEL_TITLE"]
    
################################ Finally end ##########################################################
