from __future__ import print_function
import os, re
import numpy as np
from ipywidgets import interactive, Layout, Button, Box, HBox, VBox, Text, Dropdown, Label, IntSlider, Textarea, Accordion, ToggleButton, ToggleButtons, Select, HTMLMath, FloatRangeSlider, Output, Tab
from IPython.display import display, clear_output, HTML
import json
import systemdata

from agave import *
from setvar import *
from fwPlots import *
from swanPlots import *
from command import cmd
from modInput import modInput

######################## Previous ############################################################


logOp = Output()
clearLogBtn = Button(description='Clear log', button_style='primary', layout = Layout(width = '115px'))

modelTitle = Dropdown(options=['SWAN', 'Funwave-tvd','Delft3D', 'OpenFoam', 'Cactus'])
modelBox = Box([modelTitle, clearLogBtn], 
               layout = Layout(display = 'flex', flex_flow = 'row', justify_content = 'space-between', width = '100%'))

def clearLog_btn_clicked(a):
    logOp.clear_output()

clearLogBtn.on_click(clearLog_btn_clicked)

fw_para_pairs ={
    "TOTAL_TIME":"",
    "PLOT_INTV":"",
    "Mglob":"",
    "Nglob":""
}  
cac_para_pairs = {}

######################## Previous end ############################################################


######################## SWAN Input tab ############################################################

modeTbtns = ToggleButtons(options=['NONSTAT', 'STAT'])
dimTbtns = ToggleButtons(options=['TWOD', 'ONED'])
modeBox = Box([Label(value = 'MODE: '), modeTbtns, dimTbtns],layout = Layout(width = '80%', justify_content = 'space-between'))

coordTbtns = ToggleButtons(options=['SPHE', 'CART'])
spheTbtns = ToggleButtons(options=['None', 'CCM', 'QC'])
coordBox = Box([Label(value = 'COOR:'), coordTbtns, spheTbtns],
               layout = Layout(width = '96.8%', justify_content = 'space-between'))

setTbtns = ToggleButtons(options=['NAUT', 'CART'])
setBox = Box([Label(value = 'SET:'), setTbtns],layout = Layout(width = '42.5%', justify_content = 'space-between'))

fricTbtns = ToggleButtons(options=['JONSWAP', 'COLL', 'MADS'])
fricText = Text(value = '0.067', layout = Layout(width='60px'))
fricTxtBox = Box([fricText, HTMLMath(value = r"\(m^2\)/\(s^3\)")])
fricBox = Box([Label(value = 'FRICTION:'), fricTbtns, fricTxtBox],
              layout = Layout(width = '72%', justify_content = 'space-between'))

modeStartBox = Box([modeBox, coordBox, setBox, fricBox], layout = Layout(flex_flow = 'column'))

propTbtns = ToggleButtons(options=['BSBT', 'GSE'])
propBox = Box([Label(value = 'PROP:'), propTbtns],layout = Layout(width = '42.4%', justify_content = 'space-between'))

gen3Tbtns = ToggleButtons(options=['KOMEN', 'JANS', 'WESTH'])
gen3Box = Box([Label(value = 'GEN3:'), gen3Tbtns],layout = Layout(width = '59.3%', justify_content = 'space-between'))

modelInputBox = Box([propBox, gen3Box], layout = Layout(flex_flow = 'column'))


timeBtns = ToggleButtons(options=['0.5', '1', '2'])
timeBox = Box([Label(value = 'Time Step (h):', layout = Layout(width = '98px')), timeBtns], layout = Layout(width = '90%'))


table = ['TIME','XP', 'YP', 'DEP', 'WIND', 'HS', 'DIR', 'RTP', 'PER', 'TM01', 'TM02', 'PDIR']

table_items = []
for i in range(len(table)):
    name = table[i].lower()+'Btn'
    name = ToggleButton(value = True,description = table[i])
    table_items.append(name)
    
tableBtnsBox = Box(table_items,layout = Layout(width = '90%', justify_content = 'space-between'))
tableBox = Box([Label(value = 'Table :', layout = Layout(width = '103px')), tableBtnsBox],layout = Layout(width = '90%'))
               
sp1dTbtn = ToggleButton(value = True,description = 'spec1d')
sp2dTbtn = ToggleButton(value = False,description = 'spec2d')
specBox = Box([Label(value = 'Spectral :', layout = Layout(width = '100px')), sp1dTbtn, sp2dTbtn], 
              layout = Layout(width = '90%'))

windTbtn = ToggleButton(value = True,description = 'wind')
hsTbtn = ToggleButton(value = True,description = 'hs')
dirTbtn = ToggleButton(value = False,description = 'dir')
perTbtn = ToggleButton(value = False,description = 'per')
blockBox = Box([Label(value = 'Block :', layout = Layout(width = '100px')), windTbtn, hsTbtn, dirTbtn, perTbtn], 
               layout = Layout(width = '90%'))    
    
outputRequestBox = Box([timeBox, tableBox, specBox, blockBox], layout = Layout(flex_flow = 'column'))

swanInputAcd = Accordion(children = [modeStartBox,modelInputBox,outputRequestBox], layout= Layout(width = '100%'))
swanInputAcd.set_title(0,'Model Start-up')
swanInputAcd.set_title(1,'Model Input')
swanInputAcd.set_title(2,'Output Requests')

SwanUpInputBtn = Button(description='Update Input File',button_style='primary', layout=Layout(width='100%'))

def swanupdate_btn_clicked(a):
    with logOp:
        cmd("tar -zxvf input_swan.tgz")
        cmd("mv input_swan/INPUT input_swan/INPUT_template")
    
    # set sphe method
    # for CART, there is no method needed. 
    # for SPHE, there are CCM and QC option. 
    if spheTbtns.value == "None":
        spheMethod = ""
    else:
        spheMethod = spheTbtns.value
        
    table_vars = ""
    for i in range (len(table_items)):
        if table_items[i].value == True:
            table_vars += ' '+table_items[i].description
        
    name_value_pairs = {
        "MODE"      : modeTbtns.value+' '+dimTbtns.value,
        "COORD"     : coordTbtns.value+' '+spheMethod,
        "SET"       : setTbtns.value,
        "FRICTION"  : fricTbtns.value+' '+fricText.value,
        "PROP"      : propTbtns.value,
        "GEN3"      : gen3Tbtns.value+' AGROW',
        "TIME_STEP" : timeBtns.value+' HR',
        "TABLE"     : table_vars,
        "SPEC1D"    : sp1dTbtn.value,
        "SPEC2D"    : sp2dTbtn.value,
        "WIND"      : windTbtn.value,
        "HS"        : hsTbtn.value,
        "DIR"       : dirTbtn.value,
        "PER"       : perTbtn.value
    }
    with open("input_swan/INPUT_template","r") as template:
        with open("input_swan/INPUT","w+") as ipt:
            for line in template.readlines():
                g = re.match("^(MODE|COORD|SET|FRICTION|PROP|GEN3)\s*",line)
                h = re.match("^(TABLE)(\s*\S*\s\S*\s*\S*)[\w\s]*(OUT\s\S*)(\s*\d\s*\w*)",line)
                r = re.match("(^(SPEC|BLOCK)[\s\S]*(SPEC1D|SPEC2D|WIND|HS|DIR|PER)[\s\S]*)(\s*\d\s*\w*)",line)
                s = re.match("^(COMPUTE)\s\S*\s*(\d*\.\d*)\s*(\d\s\S*)\s*(\d*\.\d*)",line)
                if g: 
                    name = g.group(1)
                    if name in name_value_pairs:
                        ipt.write(name+" "+name_value_pairs[name]+"\n")
                elif h:
                    ipt.write(h.group(1)+h.group(2)+name_value_pairs[h.group(1)]+' '+h.group(3)
                              +' '+name_value_pairs['TIME_STEP']+"\n")
                elif r:
                    if name_value_pairs[r.group(3)] == True:
                        ipt.write(r.group(1)+name_value_pairs['TIME_STEP']+"\n")
                    else:
                        ipt.write("$"+r.group(0)+"\n")
                elif s:
                    ipt.write(s.group(1)+' '+modeTbtns.value+' '+s.group(2)+' '+name_value_pairs['TIME_STEP']
                              +' '+s.group(4)+"\n")
                else:
                    ipt.write(line)
            ipt.close()
        template.close()
   
    SwanInputArea.value = open("input_swan/INPUT","r").read()
    
SwanUpInputBtn.on_click(swanupdate_btn_clicked)

SwanInputArea = Textarea(layout= Layout(height = "300px",width = '100%'))

SwanInputBox = Box([swanInputAcd, SwanUpInputBtn, SwanInputArea], 
                 layout = Layout(flex_flow = 'column', align_items = 'center'))

######################## SWAN Input tab end############################################################



##################################### Funwave-tvd Input tab ################################


fwInputdd=Dropdown(options=['Choose Input Template','Basic Template'], value='Choose Input Template')


parvals = {}
inputBox = Box(layout = Layout(flex_flow = 'column'))

def fw_on_change(change):
    inputTmp = ''
    items = []
    if change['type'] == 'change' and change['name'] == 'value':
        if(change['new'] == 'Choose Input Template'):
            items=[]
            inputBox.children = items
            return
        if(change['new'] == 'Basic Template'):
            with logOp:
                cmd("tar -zxvf input_funwave.tgz")
            inputTmp = 'input_funwave/basic_template.txt'
    
        with open(inputTmp,"r") as fd:
            for line in fd.readlines():
                g = re.search(r'(\w+)\s*=\s*\${(.*)}',line)
                if g:
                    for match in re.findall(r'(\w+)=("[^"]*"|\'[^\']*|[^,\n]*)',g.group(2)):
                        if match[0] == 'value':
                            label = line.split()[0]+'Label'
                            label = Label(value = line.split()[0].upper()+":")
                            text = line.split()[0]
                            text = Text(value=match[1])
                            box = line.split()[0]+'Box'
                            box = Box([label, text],layout = Layout(width = '100%', justify_content = 'space-between'))
                            items.append(box)
                        if match[0] == 'option':
                            label = line.split()[0]+'Label'
                            label = Label(value = line.split()[0].upper()+":")
                            togBtns = line.split()[0]
                            togBtns = ToggleButtons(options=['T', 'F'])
                            box = line.split()[0]+'Box'
                            box = Box([label, togBtns], layout = Layout(width = '100%', justify_content = 'space-between')) 
                            items.append(box)
                        
        inputBox.children = items
    
fwInputdd.observe(fw_on_change)
  
def fwUpInput_btn_clicked(a):
    inputTmp = ''
    if(fwInputdd.value == 'Basic Template'):
        inputTmp = 'input_funwave/basic_template.txt'
        
    with open("input_funwave/input_tmp.txt", "w") as fw:
        with open(inputTmp, "r") as fd:
            k=0
            for line in fd.readlines():
                g = re.search(r'(\w+)\s*=\s*\${(.*)}',line)
                if g:
                    print("%s = %s" % (g.group(1),inputBox.children[k].children[1].value),file=fw)
                    k+=1
                else:
                    print(line, end='', file=fw)
     
    fwInputArea.value = open("input_funwave/input_tmp.txt","r").read()
    surfaceFrame.max = int(float(inputBox.children[2].children[1].value)/float(inputBox.children[3].children[1].value))
    with open("input_funwave/input_tmp.txt", "r") as fw:
            for line in fw.readlines():
                g = re.search(r'(\w+)\s*=\s*(\S+)',line)
                if g:
                    para = g.group(1)
                    value = g.group(2)
                    if para in fw_para_pairs:
                        fw_para_pairs[para] = value  
    
     
fwUpInputBtn = Button(description='Update Input File',button_style='primary', layout=Layout(width='100%'))
fwUpInputBtn.on_click(fwUpInput_btn_clicked)

fwInputArea = Textarea(layout= Layout(height = "300px",width = '100%'))
fwInputBox = Box([fwInputdd, inputBox, fwUpInputBtn, fwInputArea], 
                  layout = Layout(flex_flow = 'column', align_items = 'center'))

##################################### Funwave-tvd Input tab end ###############################

##################################### Cactus Input tab ################################


cacInputdd=Dropdown(options=['Choose Input Template','Basic Template'], value='Choose Input Template')


parvals = {}
inputBox = Box(layout = Layout(flex_flow = 'column'))

def cac_on_change(change):
    inputTmp = ''
    items = []
    if change['type'] == 'change' and change['name'] == 'value':
        if(change['new'] == 'Choose Input Template'):
            items=[]
            inputBox.children = items
            return
        if(change['new'] == 'Basic Template'):
            with logOp:
                cmd("tar -zxvf input_cactus.tgz")
            inputTmp = 'input_cactus/basic_template.txt'
    
        with open(inputTmp,"r") as fd:
            for line in fd.readlines():
                g = re.search(r'(\w+)\s*=\s*\${(.*)}',line)
                if g:
                    for match in re.findall(r'(\w+)=("[^"]*"|\'[^\']*|[^,\n]*)',g.group(2)):
                        if match[0] == 'value':
                            label = line.split()[0]+'Label'
                            label = Label(value = line.split()[0].upper()+":")
                            text = line.split()[0]
                            text = Text(value=match[1])
                            box = line.split()[0]+'Box'
                            box = Box([label, text],layout = Layout(width = '100%', justify_content = 'space-between'))
                            items.append(box)
                        if match[0] == 'option':
                            label = line.split()[0]+'Label'
                            label = Label(value = line.split()[0].upper()+":")
                            togBtns = line.split()[0]
                            togBtns = ToggleButtons(options=['T', 'F'])
                            box = line.split()[0]+'Box'
                            box = Box([label, togBtns], layout = Layout(width = '100%', justify_content = 'space-between')) 
                            items.append(box)
                        
        inputBox.children = items
    
cacInputdd.observe(cac_on_change)
  
def cacUpInput_btn_clicked(a):
    inputTmp = ''
    if(cacInputdd.value == 'Basic Template'):
        inputTmp = 'input_cactus/basic_template.txt'
        
    with open("input_cactus/input_tmp.txt", "w") as fw:
        with open(inputTmp, "r") as fd:
            k=0
            for line in fd.readlines():
                g = re.search(r'(\w+)\s*=\s*\${(.*)}',line)
                if g:
                    print("%s = %s" % (g.group(1),inputBox.children[k].children[1].value),file=fw)
                    k+=1
                else:
                    print(line, end='', file=fw)
     
    cacInputArea.value = open("input_cactus/input_tmp.txt","r").read()
    print("inputBox.children[3].children[1].value=",float(inputBox.children[3].children[1].value))
    #surfaceFrame.max = int(float(inputBox.children[2].children[1].value)/float(inputBox.children[3].children[1].value))
    with open("input_cactus/input_tmp.txt", "r") as fw:
            for line in fw.readlines():
                g = re.search(r'(\w+)\s*=\s*(\S+)',line)
                if g:
                    para = g.group(1)
                    value = g.group(2)
                    cac_para_pairs[para] = value  
    
     
cacUpInputBtn = Button(description='Update Cactus Input File',button_style='primary', layout=Layout(width='100%'))
cacUpInputBtn.on_click(cacUpInput_btn_clicked)

cacInputArea = Textarea(layout= Layout(height = "300px",width = '100%'))
cacInputBox = Box([cacInputdd, inputBox, cacUpInputBtn, cacInputArea], 
                  layout = Layout(flex_flow = 'column', align_items = 'center'))

##################################### Cactus Input tab end ###############################





##################################### Delft3D Input tab ######################################

delft3d_items=[Label(value='Coming soon', layout = Layout(width = '200px'))]   
delft3dBox = Box(delft3d_items, layout= Layout(flex_flow = 'column', align_items='stretch', disabled=False))

##################################### Delft3D Input tab end ###############################






##################################### OpenFoam Input tab ######################################

ofCaseName = Text()

ofInputBox = Box([Label(value = 'Case Name') , ofCaseName], 
                 layout = Layout(flex_flow = 'row', align_items = 'center'))

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

all_apps = systemdata.load()
exec_to_app = {}

machines_options = []
app0 = None
for app in all_apps:
    # If app0 is not assigned and the current
    # app is one we have permission to use
    if app0 is None and all_apps[app]["perm"] in ["RWX", "RX"]:
        app0 = app
    exec_sys = all_apps[app]["exec_sys"]
    exec_to_app[exec_sys] = app
    machines_options += [exec_sys]

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
machines.value = all_apps[app0]["exec_sys"]
on_machine_value_set(None)

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

    if (modelTitle.value == "Funwave-tvd"): 
        with logOp:
            cmd("mv input_funwave/input_tmp.txt input_funwave/input.txt")
            modInput(procs[0], "input_funwave/input.txt")
            cmd("rm -fr input")
            cmd("mkdir input")
            cmd("cp input_funwave/input.txt input")
            cmd("cp input_funwave/depth.txt input")
            cmd("tar cvzf input.tgz input")
            setvar("INPUT_DIR=${AGAVE_USERNAME}_$(date +%Y-%m-%d_%H-%M-%S)")
            cmd("files-mkdir -S ${STORAGE_MACHINE} -N inputs/${INPUT_DIR}")
            cmd("files-upload -F input.tgz -S ${STORAGE_MACHINE} inputs/${INPUT_DIR}/")

            submitJob(nodes, procs[0], "funwave", jobNameText.value, machines.value, queues.value)

    elif (modelTitle.value == "Cactus"): 
        with logOp:
            cmd("mv input_cactus/input_tmp.txt input_cactus/input.txt")
            modInput(procs[0], "input_funwave/input.txt")
            cmd("rm -fr input")
            cmd("mkdir input")
            cmd("cp input_cactus/input.txt input")
            cmd("cp input_cactus/depth.txt input")
            cmd("tar cvzf input.tgz input")
            setvar("INPUT_DIR=${AGAVE_USERNAME}_$(date +%Y-%m-%d_%H-%M-%S)")
            cmd("files-mkdir -S ${STORAGE_MACHINE} -N inputs/${INPUT_DIR}")
            cmd("files-upload -F input.tgz -S ${STORAGE_MACHINE} inputs/${INPUT_DIR}/")

            submitJob(nodes, procs[0], "cactus", jobNameText.value, machines.value, queues.value)

        
    elif (modelTitle.value == "SWAN"): 
        with logOp:
            if not os.path.exists("input_swan"):
                cmd("tar -zxvf input_swan.tgz")
            cmd("rm -fr input")
            cmd("cp -r input_swan input")
            cmd("tar cvzf input.tgz input")
            setvar("INPUT_DIR=${AGAVE_USERNAME}_$(date +%Y-%m-%d_%H-%M-%S)")
            cmd("files-mkdir -S ${STORAGE_MACHINE} -N inputs/${INPUT_DIR}")
            cmd("files-upload -F input.tgz -S ${STORAGE_MACHINE} inputs/${INPUT_DIR}/")
            submitJob(numXSlider.value, numYSlider.value, "swan", jobNameText.value, machines.value, queues.value) 
    
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
        cout = cmd("jobs-list -l 10")
        out1 = cout["stdout"]
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
            rcmd = "jobs-output-list "+ jobid
            cout = cmd(rcmd)
            out1 = cout["stdout"]
            outputSelect.options = out1
    
jobOutputBtn.on_click(jobOutput_btn_clicked)

def download_btn_clicked(a):
    with logOp:
        try:
            g = re.match(r'^\S+',jobSelect.value)
            jobid = g.group(0)
            if(outputSelect.value.find('.')==-1):
                rcmd = "jobs-output-get -r "+ jobid +" "+ outputSelect.value
            else:
                rcmd = "jobs-output-get "+ jobid +" "+ outputSelect.value
        
            print (rcmd)
            os.system(rcmd)
        
            if(outputSelect.value == 'output.tar.gz'):
                cmd("rm -fr output")
                rcmd = 'tar -zxvf output.tar.gz'
                cmd(rcmd)
            elif(re.match(r'.*\.(txt|out|err|ipcexe)',outputSelect.value)):
                with open(outputSelect.value,'r') as fd:
                    for line in fd.readlines():
                        print(line,end='')
            else:
                print('value=(',outputSelect.value,')',sep='')
        except Exception as ex:
            print("DIED!",ex)

downloadOpBtn.on_click(download_btn_clicked)

def jobHis_btn_clicked(a):
    g = re.match(r'^\S+', jobSelect.value)
    with logOp:
        if g:
            jobid = g.group(0)
            rcmd = "jobs-history -V " + jobid
            cout = cmd(rcmd)
            out1 = cout["stdout"]
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



################################## SWAN Visualization tab #####################################

Yoption = Dropdown(options=['Choose one','Hsig','RTpeak','PkDir','X_Windv','Y_Windv'])
plotsInter = interactive(oneDPlots, Y_axis = Yoption )
oneDBox = Box([plotsInter])

hsPreprocessBtn = Button(description='HS preprocess',button_style='primary', layout=Layout(width='auto'))
hsPreprocessBtn.on_click(hsPreprocess_btn_clicked)

hsIndex = IntSlider(value=0, min=0, max=120)
hsInter = interactive(twoDAnimate, Time_Step = hsIndex)

twoDBox = Box([hsPreprocessBtn, hsInter], layout = Layout(flex_flow = 'column', align_items='stretch'))

swanVisuAcd =Accordion(children = [oneDBox,twoDBox])
swanVisuAcd.set_title(0,'1D ')
swanVisuAcd.set_title(1,'2D ')

################################## SWAN Visualization tab end #####################################



############################### Funwave Visualization tab ##########################################


fwYoption = Dropdown(options=['Choose one','eta','u','v'])
fwplotsInter = interactive(fwOneD, Y_in_plots = fwYoption)
fwoneDBox = Box([fwplotsInter])
caconeDBox = Box([fwplotsInter])

depthBtn = Button(description='display',button_style='primary', layout=Layout(width='auto'))
depthOutput = Output()

def depth_Btn_clicked(a):
    with depthOutput:
        display(waterDepth(fw_para_pairs['Mglob'],fw_para_pairs['Nglob']))

depthBtn.on_click(depth_Btn_clicked)
depthBox = Box([Label(value='Water Depth'),depthBtn],layout = Layout(width = '80%'))

depProfileN = IntSlider(value=0, min=0, max=200)
depProfileInter = interactive(depProfile, N = depProfileN)
depProfileBox = Box([Label(value='Depth Profile Snapshot'), depProfileInter])

depProfileAnimaRange = FloatRangeSlider(value=[5,7], min=0.0, max=30, step=0.2,
                                 description='Time period (s):',readout=True,readout_format='.2f', layout = Layout(width ="60%"))
depProfileAnimBtn = Button(description='display',button_style='primary', layout=Layout(width='auto'))
depProfileAnimOutput = Output()

def depProfileAnim_Btn_clicked(a):
    anim = depProfileWithEta(depProfileAnimaRange.value[0], depProfileAnimaRange.value[1], 
                             fw_para_pairs['TOTAL_TIME'], fw_para_pairs['PLOT_INTV'], fw_para_pairs['Mglob'])
    depProfileAnimOutput.clear_output()
    with depProfileAnimOutput:
        display(HTML(anim.to_html5_video()))
depProfileAnimBtn.on_click(depProfileAnim_Btn_clicked)
depProfileAnimBox = Box([Label(value='Cross-shore profile animation'), depProfileAnimaRange, depProfileAnimBtn], 
                  layout = Layout(width = '80%', justify_content = 'space-between'))


twoDsnapFrame = IntSlider(value=0, min=0, max=151)
twoDsnapInter = interactive(twoDsnapPlot, frame = twoDsnapFrame)
twoDsnapBox = Box([Label(value='Surface Elevation snapshot'),twoDsnapInter])

twoDanimRange = FloatRangeSlider(value=[5,7], min=0.0, max=30, step=0.2,
                                 description='Time period (s):',readout=True,readout_format='.2f', layout = Layout(width ="60%"))
twoDanimBtn = Button(description='display',button_style='primary', layout=Layout(width='auto'))
twoDanimOutput = Output()
def twoDanim_Btn_clicked(a):
    anim = twoDsnapAnim(twoDanimRange.value[0],twoDanimRange.value[1], fw_para_pairs['PLOT_INTV'])
    twoDanimOutput.clear_output()
    with twoDanimOutput:
        display(HTML(anim.to_html5_video()))
twoDanimBtn.on_click(twoDanim_Btn_clicked)
twoDanimBox = Box([Label(value='Surface Elevation animation'), twoDanimRange, twoDanimBtn], 
                  layout = Layout(width = '80%', justify_content = 'space-between'))

basicBtn = Button(description='display',button_style='primary', layout=Layout(width='auto'))
basicOutput = Output()

def basic_Btn_clicked(a):
    frames = []
    for i in range(1,surfaceFrame.max):
        frames += [np.genfromtxt("output/output/eta_%05d" % i)]
    anim = basicAnimation(frames)
    with basicOutput:
        display(HTML(anim.to_html5_video()))

basicBtn.on_click(basic_Btn_clicked)
basicBox = Box([Label(value='Surface Elevation animation 2'),basicBtn], layout = Layout(width = '80%'))


basicAnimBox = Box([depthBox, depthOutput,depProfileBox, depProfileAnimBox, depProfileAnimOutput, 
                    twoDsnapBox, twoDanimBox, twoDanimOutput],
                   layout = Layout(flex_flow = 'column', align_items='stretch',))

surfaceFrame = IntSlider(value=0, min=0, max=31)
surfaceInter = interactive(surfacePlot, frame = surfaceFrame)
surfaceBox = Box([Label(value='Surface Elevation snapshot'),surfaceInter])

rotatingBtn = Button(description='display',button_style='primary', layout=Layout(width='auto'))
rotatingOutput = Output()

def rotating_Btn_clicked(a):
    frames = []
    for i in range(1,surfaceFrame.max):
        frames += [np.genfromtxt("output/output/eta_%05d" % i)]
    anim = rotatingAnimation(frames)
    with rotatingOutput:
        display(HTML(anim.to_html5_video()))

rotatingBtn.on_click(rotating_Btn_clicked)
rotatingBox = Box([Label(value='Surface Elevation animation'),rotatingBtn], layout = Layout(width = '80%'))
rotatingAnimBox = Box([surfaceBox, rotatingBox, rotatingOutput], layout = Layout(flex_flow = 'column', align_items='stretch'))

fwVisuAcd = Accordion([fwoneDBox, basicAnimBox,rotatingAnimBox])
fwVisuAcd.set_title(0,'1D')
fwVisuAcd.set_title(1,'2D')
fwVisuAcd.set_title(2,'3D')

cacVisuAcd = Accordion([caconeDBox, basicAnimBox,rotatingAnimBox])
cacVisuAcd.set_title(0,'1D')
cacVisuAcd.set_title(1,'2D')
cacVisuAcd.set_title(2,'3D')

############################### Funwave Visualization tab end ##########################################






############################### Delft3D Visualization tab    ##########################################

delft3d_visu=[Label(value='Coming soon', layout = Layout(width = '200px'))]   
delft3dVisuBox = Box(delft3d_items, layout= Layout(flex_flow = 'column', align_items='stretch', disabled=False))



############################### Delft3D Visualization tab end ##########################################







############################### OpenFoam Visualization tab    ##########################################

openfoam_visu=[Label(value='Coming soon', layout = Layout(width = '200px'))]   
openfoamVisuBox = Box(delft3d_items, layout= Layout(flex_flow = 'column', align_items='stretch', disabled=False))


############################### OpenFoam Visualization tab end ##########################################








################################ Finally ##########################################################
        
tab_nest = Tab()
tab_nest.children = [SwanInputBox, runBox, outputBox, swanVisuAcd]
tab_nest.set_title(0, 'Input')
tab_nest.set_title(1, 'Run')
tab_nest.set_title(2, 'Output')
tab_nest.set_title(3, 'Visualization')

setvar("""PATH=$HOME/agave-model/bin:$PATH""")
cmd("auth-tokens-refresh")
clear_output()

def on_change(change):
    setvar("MODEL_TITLE="+modelTitle.value)
    if change['type'] == 'change' and change['name'] == 'value':
        if(change['new'] == 'SWAN'):
            out.clear_output()
            with out:
                tab_nest.children = [SwanInputBox, runBox, outputBox, swanVisuAcd]
                display(tab_nest)
        if(change['new'] == 'Funwave-tvd'):
            out.clear_output()
            with out:
                tab_nest.children = [fwInputBox, runBox, outputBox, fwVisuAcd]
                display(tab_nest)
        if(change['new'] == 'Cactus'):
            out.clear_output()
            with out:
                tab_nest.children = [cacInputBox, runBox, outputBox, cacVisuAcd]
                display(tab_nest)
        if(change['new'] == 'Delft3D'):
            out.clear_output()
            with out:
                tab_nest.children = [delft3dBox, runBox, outputBox, delft3dVisuBox]
                display(tab_nest)
        if(change['new'] == 'OpenFoam'):
            out.clear_output()
            with out:
                tab_nest.children = [ofInputBox, runBox, outputBox, openfoamVisuBox]
                display(tab_nest)
           
modelTitle.observe(on_change)

display(modelBox)

out = Output()

with out:
    display(tab_nest)
    
display(out)

display(logOp)

if "MODEL_TITLE" in os.environ:
    modelTitle.value = os.environ["MODEL_TITLE"]

################################ Finally end ##########################################################
