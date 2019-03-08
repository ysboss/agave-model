from __future__ import print_function
import os, re
import numpy as np
from ipywidgets import interactive, Layout, Button, Box, HBox, VBox, Text, Dropdown, Label, IntSlider, Textarea, Accordion, ToggleButton, ToggleButtons, Select, HTMLMath, FloatRangeSlider, Output, Tab, Checkbox
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

cur_model = 'swan'
logOp = Output()
logStash = Output()   # use to receive logs that are stashed for user
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

def generatePara(templateFile):
    items = []
    with open(templateFile, 'r') as fd:
        for line in fd.readlines():
            g = re.search(r'[\w:]*\s*.*=*\s*\${(.*)}',line)
            if g:
                label_value = ''
                isTB = False
                for match in re.findall(r'(\w+)=("[^"]*"|\'[^\']*|[^,\n]*)', g.group(1)):
                    if match[0] == 'label':
                        lbs = match[1].split('/')
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
    fd.close()
    return items

def updatePara(templateFile, newInput, inputBox):
    
    with open(newInput, "w") as fw:
        with open(templateFile, "r") as fd:
            count = 0
            for line in fd.readlines():
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
        fd.close()
    fw.close()    
    
    
def template_on_change(change):
    inputTmp = ''
    if change['type'] == 'change' and change['name'] == 'value':
        if(change['new'] == 'Choose Input Template'):
            tab_nest.children[0].children[2].children = []
            return
        if(change['new'] == 'Basic Template'):
            with logOp:
                cmd("tar -zxvf input_" + cur_model + ".tgz")
            inputTmp = 'input_' + cur_model + '/basic_template.txt'
        if(change['new'] == 'HDF5 Template'):
            with logOp:
                cmd("tar -zxvf input_" + cur_model + ".tgz")
            inputTmp = 'input_' + cur_model + '/hdf5_template.txt'
        
        tab_nest.children[0].children[2].children = generatePara(inputTmp)
        
        
def update_btn_clicked(a):
    if (tab_nest.children[0].children[1].value == True):
        with logOp:
            cmd("rm -f input.tgz")
            cmd("rm -fr input")
            cmd("cp -f ../input_" + cur_model + ".tgz input.tgz")
            return
        
    newInput = 'input_'+ cur_model + '/input_tmp.txt'
    inputTmp = ''
    if(tab_nest.children[0].children[0].value == 'Basic Template'):
        inputTmp = 'input_' + cur_model + '/basic_template.txt'
    if(tab_nest.children[0].children[0].value == 'HDF5 Template'):
        inputTmp = 'input_' + cur_model + '/basic_template.txt'
    
    updatePara(inputTmp, newInput, tab_nest.children[0].children[2])
    
    tab_nest.children[0].children[4].value = open(newInput, 'r').read()
  
             
    



######################## Previous end ############################################################

######################## SWAN Input tab ############################################################

swanInputdd = Dropdown(options=['Choose Input Template','Basic Template'], value='Choose Input Template')
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





##################################### Delft3D Input tab ######################################

delft3d_items=[Label(value='Coming soon', layout = Layout(width = '200px'))]   
delft3dBox = Box(delft3d_items, layout= Layout(flex_flow = 'column', align_items='stretch', disabled=False))

##################################### Delft3D Input tab end ###############################






##################################### OpenFoam Input tab ######################################

ofCaseName = Dropdown()
ofCbox = Checkbox(value = False, description = "Use Own Input")
cases = ["Select Input Case"]

with logStash:
    cmd("tar -zxvf input_openfoam.tgz")
    with open("input_openfoam/cases.txt", 'r') as fr:
        lines = fr.readlines()
        for line in lines:
            cases.append(line)
        ofCaseName.options = cases       

def ofUpInput_btn_clicked(a):
    if (ofCbox.value == True):
        with logOp:
            cmd("rm -f input.tgz")
            cmd("rm -fr input")
            cmd("cp -f ../input_openfoam.tgz input.tgz")
            return
        
    if not ofCaseName.value == "Select Input Case":
        with open("input_openfoam/" + ofCaseName.value[:-1] + "/system/decomposeParDict", "r") as fd:
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
   
ofInputBox = Box([ofCaseName, ofCbox, ofUpInputBtn, ofInputArea], 
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

def modify_openfoam(case):
    sp = case.split('/')
    caseName = sp[len(sp)-1]
    tmp = ""
    with open("input/system/decomposeParDict", "r") as fd:
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
            cmd("rm -fr input") 
            cmd("mkdir input")
            if (cur_model == "swan"):
                cmd("mv input_" + cur_model + "/input_tmp.txt input_" + cur_model + "/INPUT")
                cmd("cp -rT input_" + cur_model + " input")
            if (cur_model == "funwave" or cur_model == "cactus"):
                cmd("mv input_" + cur_model + "/input_tmp.txt input_" + cur_model + "/input.txt")
                modInput(procs[0], "input_funwave/input.txt")
                cmd("cp input_" + cur_model + "/input.txt input")
                cmd("cp input_" + cur_model + "/depth.txt input")
            if (cur_model == "openfoam"):
                cmd("cp -a input_" + cur_model + "/"+ofCaseName.value[:-1]+"/. input")
                modify_openfoam(ofCaseName.value)
                
            cmd("tar cvzf input.tgz input")
            
        setvar("INPUT_DIR=${AGAVE_USERNAME}_$(date +%Y-%m-%d_%H-%M-%S)")
        cmd("files-mkdir -S ${STORAGE_MACHINE} -N inputs/${INPUT_DIR}")
        cmd("files-upload -F input.tgz -S ${STORAGE_MACHINE} inputs/${INPUT_DIR}/")
        submitJob(nodes, procs[0], cur_model, jobNameText.value, machines.value, queues.value)
        
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
                cmd("mkdir -p output_" + jobid)
                cmd('tar -zxvf output.tar.gz -C ' + jobid)
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
tab_nest.children = [swanInputBox, runBox, outputBox, swanVisuAcd]
tab_nest.set_title(0, 'Input')
tab_nest.set_title(1, 'Run')
tab_nest.set_title(2, 'Output')
tab_nest.set_title(3, 'Visualization')

setvar("""PATH=$HOME/agave-model/bin:$PATH""")
cmd("auth-tokens-refresh")
clear_output()

def on_change(change):
    global cur_model
    with logOp:
        setvar("MODEL_TITLE="+modelTitle.value)
    if change['type'] == 'change' and change['name'] == 'value':
        if(change['new'] == 'SWAN'):
            cur_model = 'swan'
            out.clear_output()
            with out:
                tab_nest.children = [swanInputBox, runBox, outputBox, swanVisuAcd]
                display(tab_nest)
                
        if(change['new'] == 'Funwave-tvd'):
            cur_model = 'funwave'
            out.clear_output()
            with out:
                tab_nest.children = [fwInputBox, runBox, outputBox, fwVisuAcd]
                display(tab_nest)
        if(change['new'] == 'Cactus'):
            cur_model = 'cactus'
            out.clear_output()
            with out:
                tab_nest.children = [cacInputBox, runBox, outputBox, cacVisuAcd]
                display(tab_nest)
        if(change['new'] == 'Delft3D'):
            cur_model = 'delft3d'
            out.clear_output()
            with out:
                tab_nest.children = [delft3dBox, runBox, outputBox, delft3dVisuBox]
                display(tab_nest)
        if(change['new'] == 'OpenFoam'):
            cur_model = 'openfoam'
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
