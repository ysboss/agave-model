from __future__ import print_function
from ipywidgets import interact, interactive, fixed, interact_manual, Layout, Button, Box,VBox, HBox, FloatText, Text, Dropdown, Label, IntSlider, Textarea, Accordion, ToggleButton, ToggleButtons, Select, RadioButtons, HTMLMath, FloatRangeSlider
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
from matplotlib import animation, rc
from mpl_toolkits.mplot3d import Axes3D

#from pylab import *
import matplotlib.pyplot as plt2
import sys
import numpy as np
import os
import re
#from upload import upload_widget, set_input

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import date2num
import time
from datetime import datetime
import datetime


from agave import *
from setvar import *

from shutil import copyfile

from fwPlots import *
from swanPlots import *

from command import cmd


######################## Previous ############################################################

input_item_layout = Layout(
    display = 'flex',
    flex_flow = 'row',
    justify_content = 'flex-start',
    width = '50%'
)
  

modelTitle = Dropdown(options=['SWAN', 'Funwave-tvd','Delft3D'])
modelBox = Box([Label(value='Model', layout = Layout(width = '100px')), modelTitle], layout = input_item_layout)


delft3d_items=[Label(value='Coming soon', layout = Layout(width = '200px'))]   
delft3dBox = Box(delft3d_items, layout= Layout(
 #   display = 'flex',
    flex_flow = 'column',
    align_items='stretch',
    disabled=False
))

######################## SWAN Input tab ############################################################

modeTbtns = ToggleButtons(options=['NONSTAT', 'STAT'])
dimTbtns = ToggleButtons(options=['TWOD', 'ONED'])
modeBox = Box([Label(value = 'MODE: '), modeTbtns, dimTbtns],layout = Layout(width = '80%', justify_content = 'space-between'))

coordTbtns = ToggleButtons(options=['SPHE', 'CART'])
spheTbtns = ToggleButtons(options=['CCM', 'QC'])
coordBox = Box([Label(value = 'COOR:'), coordTbtns, spheTbtns],
               layout = Layout(width = '80%', justify_content = 'space-between'))

setTbtns = ToggleButtons(options=['NAUT', 'CART'])
setBox = Box([Label(value = 'SET:'), setTbtns],layout = Layout(width = '42.4%', justify_content = 'space-between'))

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
    cmd("tar -zxvf input_swan.tgz")
    cmd("mv input_swan/INPUT input_SWAN/INPUT_template")
    table_vars = ""
    for i in range (len(table_items)):
        if table_items[i].value == True:
            table_vars += ' '+table_items[i].description
        
    name_value_pairs = {
        "MODE"      : modeTbtns.value+' '+dimTbtns.value,
        "COORD"     : coordTbtns.value+' '+spheTbtns.value,
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
    with open("input_SWAN/INPUT_template","r") as template:
        with open("input_SWAN/INPUT","w+") as ipt:
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
   
    SwanInputArea.value = open("input_SWAN/INPUT","r").read()
    
SwanUpInputBtn.on_click(swanupdate_btn_clicked)

SwanInputArea = Textarea(layout= Layout(height = "300px",width = '100%'))


SwanInputBox = Box([swanInputAcd, SwanUpInputBtn, SwanInputArea], 
                 layout = Layout(flex_flow = 'column', align_items = 'center'))

 






##################################### Funwave-tvd Input tab ################################


# totalTimeText = Text()
# totalTimeBox = Box([Label(value = 'Total Computational Time (s)'), totalTimeText],
#                    layout = Layout(width = '55%', justify_content = 'space-between'))

# plotTimeText = Text()
# plotTimeBox = Box([Label(value = 'Plot Interval (s)'), plotTimeText],
#                   layout = Layout(width = '55%', justify_content = 'space-between'))

# timeBox = Box([totalTimeBox, plotTimeBox],layout = Layout(flex_flow = 'column'))

# etaTbtns = ToggleButtons(options=['True', 'False'])
# etaBox = Box([Label(value = 'Surface Elevation'), etaTbtns],layout = Layout(width = '50%', justify_content = 'space-between'))

# uTbtns = ToggleButtons(options=['True', 'False'])
# uBox = Box([Label(value = 'U'), uTbtns ],layout = Layout(width = '50%', justify_content = 'space-between'))

# vTbtns = ToggleButtons(options=['True', 'False'])
# vBox = Box([Label(value = 'V'), vTbtns],layout = Layout(width = '50%', justify_content = 'space-between'))

# outputBox = Box([etaBox, uBox, vBox], layout = Layout(flex_flow = 'column'))

# fwInputAcd = Accordion(children = [timeBox,outputBox], layout= Layout(width = '100%'))
# fwInputAcd.set_title(0,'Time')
# fwInputAcd.set_title(1,'Output')

# fwUpInputBtn = Button(description='Update Input File',button_style='primary', layout=Layout(width='100%'))

# def convertTF(value):
#     if (value == "True"):
#         return "T"
#     elif (value == "False"):
#         return "F"
#     else:
#         return value

# def fwupdate_btn_clicked(a):
#     cmd("tar -zxvf input_funwave.tgz")
#     cmd("mv input_funwave/input.txt input_funwave/input_template.txt")
#     name_value_pairs = {
#         "TOTAL_TIME": totalTimeText.value,
#         "PLOT_INTV" : plotTimeText.value,
#         "ETA"       : convertTF(etaTbtns.value),
#         "U"          : convertTF(uTbtns.value),
#         "V"          : convertTF(vTbtns.value)
#     }
#     with open("input_funwave/input_template.txt","r") as template:
#         with open("input_funwave/input_tmp.txt","w+") as inputTmp:
#             for line in template.readlines():
#                 g = re.match("^(TOTAL_TIME|PLOT_INTV|ETA|U|V)\s*=\s*(\S+)",line)
#                 if g:
#                     name = g.group(1)
#                     if name in name_value_pairs:
#                         inputTmp.write(name+" = "+name_value_pairs[name]+"\n")
#                 else:
#                     inputTmp.write(line)
#             inputTmp.close()
#         template.close()
#     fwInputArea.value = open("input_funwave/input_tmp.txt","r").read()
#     surfaceFrame.max = int(float(totalTimeText.value))/int(float(plotTimeText.value))
# fwUpInputBtn.on_click(fwupdate_btn_clicked)

# fwInputArea = Textarea(layout= Layout(height = "300px",width = '100%'))

# fwInputBox = Box([fwInputAcd, fwUpInputBtn, fwInputArea], 
#                  layout = Layout(flex_flow = 'column', align_items = 'center'))


############Create paras gui###############

fwInputdd=Dropdown(options=['Choose Input Template','Basic template'])


parvals = {}
inputBox = Box(layout = Layout(flex_flow = 'column'))

def fw_on_change(change):
    cmd("tar -zxvf input_funwave.tgz")
    inputTmp = ''
    items = []
    if(fwInputdd.value == 'Choose Input Template'):
        return
    if(fwInputdd.value == 'Basic template'):
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
                        text = Text()
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
    if(fwInputdd.value == 'Basic template'):
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
    surfaceFrame.max = int(float(inputBox.children[0].children[1].value))/int(float(inputBox.children[1].children[1].value))
            
fwUpInputBtn = Button(description='Update Input File',button_style='primary', layout=Layout(width='100%'))
fwUpInputBtn.on_click(fwUpInput_btn_clicked)

fwInputArea = Textarea(layout= Layout(height = "300px",width = '100%'))
fwInputBox = Box([fwInputdd, inputBox, fwUpInputBtn, fwInputArea], 
                  layout = Layout(flex_flow = 'column', align_items = 'center'))





##################################### Run tab ################################
run_item_layout = Layout(
    display = 'flex',
    flex_flow = 'row',
    justify_content = 'flex-start',
    width = '50%'
)

numnodeSlider = IntSlider(value=0, min=1, max=8, step=1)
numprocSlider = IntSlider(value=0, min=1, max=16, step=1)

runBtn = Button(description='Run', button_style='primary', layout= Layout(width = '50px'))

run_items = [
    Box([Label(value='The number of nodes', layout = Layout(width = '350px')), numnodeSlider], layout = run_item_layout),
    Box([Label(value='The number of Processors of each node', layout=Layout(width = '350px')), numprocSlider], layout= run_item_layout),
    Box([runBtn]),
]

def modifyFWinput():
    name_value_pairs = {
        "PX" : str(numnodeSlider.value),
        "PY" : str(numprocSlider.value)
    }
    with open("input_funwave/input_tmp.txt","r") as tmp:
        with open("input_funwave/input.txt","w") as inputfile:
            for line in tmp.readlines():
                g = re.match("^(PX|PY)\s*=\s*(\S+)",line)
                if g:
                    name = g.group(1)
                    if name in name_value_pairs:
                        inputfile.write(name+" = "+name_value_pairs[name]+"\n")
                else:
                    inputfile.write(line)
            inputfile.close()
        tmp.close()
    
def runfun_btn_clicked(a):
    if (modelTitle.value == "SWAN"): 
        cmd("rm -fr input")
        cmd("mkdir input")
        cmd("cp -r input_swan/* input")
        cmd("tar cvzf input.tgz input")
        setvar("INPUT_DIR=${AGAVE_USERNAME}_$(date +%Y-%m-%d_%H-%M-%S)")
        cmd("files-mkdir -S ${STORAGE_MACHINE} -N ${DEPLOYMENT_PATH}/${INPUT_DIR}")
        cmd("files-upload -F input.tgz -S ${STORAGE_MACHINE} ${DEPLOYMENT_PATH}/${INPUT_DIR}/")
        submitJob(numnodeSlider.value,numprocSlider.value,"swan") 
        
    elif (modelTitle.value == "Funwave-tvd"): 
        modifyFWinput()
        cmd("rm -fr input")
        cmd("mkdir input")
        cmd("cp input_funwave/input.txt input")
        cmd("tar cvzf input.tgz input")
        setvar("INPUT_DIR=${AGAVE_USERNAME}_$(date +%Y-%m-%d_%H-%M-%S)")
        cmd("files-mkdir -S ${STORAGE_MACHINE} -N ${DEPLOYMENT_PATH}/${INPUT_DIR}")
        cmd("files-upload -F input.tgz -S ${STORAGE_MACHINE} ${DEPLOYMENT_PATH}/${INPUT_DIR}/")
        submitJob(numnodeSlider.value,numprocSlider.value,"funwave") 
    
runBtn.on_click(runfun_btn_clicked)


runBox = VBox(run_items)









################################# Output tab ###################################

jobListBtn = Button(description='List jobs history', button_style='primary', layout= Layout(width = '115px'))

jobSelect = Select(layout = Layout(height = '150px', width='100%'))

jobOutputBtn = Button(description='List job output', button_style='primary', layout= Layout(width = '115px'))

abortBtn = Button(description='Abort', button_style='danger', layout= Layout(width = 'auto'))

outputSelect = Select(layout = Layout(height = '150px', width='100%'))

downloadOpBtn = Button(description='Download', button_style='primary', layout= Layout(width = '115px'))

def jobList_btn_clicked(a):
    cout = cmd("jobs-list -l 10")
    out1 = cout["stdout"]
    jobSelect.options = out1
    
jobListBtn.on_click(jobList_btn_clicked)

def abort_btn_clicked(a):
    g = re.match(r'^\S+',jobSelect.value)
    if g:
        jobid = g.group(0)
        rcmd = "jobs-stop "+jobid
        cmd(rcmd)

abortBtn.on_click(abort_btn_clicked)


def jobOutput_btn_clicked(a):
    g = re.match(r'^\S+',jobSelect.value)
    if g:
        jobid = g.group(0)
        rcmd = "jobs-output-list "+jobid
        cout = cmd(rcmd)
        out1 = cout["stdout"]
        outputSelect.options = out1
    
jobOutputBtn.on_click(jobOutput_btn_clicked)

def download_btn_clicked(a):
    try:
        g = re.match(r'^\S+',jobSelect.value)
        jobid = g.group(0)
        if(outputSelect.value.find('.')==-1):
            rcmd = "jobs-output-get -r "+ jobid +" "+ outputSelect.value
        else:
            rcmd = "jobs-output-get "+ jobid +" "+ outputSelect.value
        cmd(rcmd)
        
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

output_items = [
    Box([jobListBtn]),
    Box([jobSelect], layout = Layout(width='50%')),
    Box([jobOutputBtn,abortBtn], layout = Layout(display = 'flex', justify_content = 'space-between', width='50%')),
    Box([outputSelect], layout = Layout(width='50%')),
    Box([downloadOpBtn])
]

outputBox = VBox(output_items)









##################################### SWAN Visualization tab ########################################

Yoption = Dropdown(options=['Choose one','Hsig','RTpeak','PkDir','X_Windv','Y_Windv'])
plotsInter = widgets.interactive(oneDPlots, Y_axis = Yoption )
oneDBox = Box([plotsInter])


hsPreprocessBtn = Button(description='HS preprocess',button_style='primary', layout=Layout(width='auto'))
hsPreprocessBtn.on_click(hsPreprocess_btn_clicked)


hsIndex = IntSlider(value=0, min=0, max=120)
hsInter = widgets.interactive(twoDAnimate, Time_Step = hsIndex)

twoDBox = Box([hsPreprocessBtn, hsInter], layout = Layout(flex_flow = 'column', align_items='stretch'))


swanVisuAcd =Accordion(children = [oneDBox,twoDBox])
swanVisuAcd.set_title(0,'1D ')
swanVisuAcd.set_title(1,'2D ')






############################### Funwave Visualization tab ##########################################


fwYoption = Dropdown(options=['Choose one','eta','u','v'])
fwplotsInter = widgets.interactive(fwOneD, Y_axis = fwYoption )
fwoneDBox = Box([fwplotsInter])


surfaceFrame = IntSlider(value=0, min=0, max=31)
surfaceInter = widgets.interactive(surfacePlot, frame = surfaceFrame)
surfaceBox = Box([Label(value='Surface Elevation snapshot'),surfaceInter])

basicBtn = Button(description='display',button_style='primary', layout=Layout(width='auto'))
basicOutput = widgets.Output()

def basic_Btn_clicked(a):
    frames = []
    for i in range(1,surfaceFrame.max):
#         frames += [np.genfromtxt("output/output/eta_%05d" % i)]
        frames += [np.genfromtxt("output/f1/eta_%05d" % i)]
    anim = basicAnimation(frames)
    with basicOutput:
        display(HTML(anim.to_html5_video()))

basicBtn.on_click(basic_Btn_clicked)
basicBox = Box([Label(value='Surface Elevation animation 2'),basicBtn], layout = Layout(width = '80%'))


depthBtn = Button(description='display',button_style='primary', layout=Layout(width='auto'))
depthOutput = widgets.Output()



def depth_Btn_clicked(a):
    #plt = waterDepth()
    with depthOutput:
        display(waterDepth())

depthBtn.on_click(depth_Btn_clicked)
depthBox = Box([Label(value='Water Depth'),depthBtn],layout = Layout(width = '80%'))


depProfileN = IntSlider(value=0, min=0, max=200)
depProfileInter = widgets.interactive(depProfile, N = depProfileN)
depProfileBox = Box([Label(value='Depth Profile Snapshot'), depProfileInter])



TwoDsnapFrame = IntSlider(value=0, min=0, max=1501)
TwoDsnapInter = widgets.interactive(TwoDsnapPlot, frame = TwoDsnapFrame)
TwoDsnapBox = Box([Label(value='Surface Elevation snapshot'),TwoDsnapInter])


TwoDanimRange = FloatRangeSlider(value=[5,7], min=0.0, max=30, step=0.02,
                                 description='Time period (s):',readout=True,readout_format='.2f', layout = Layout(width ="60%"))

TwoDanimBtn = Button(description='display',button_style='primary', layout=Layout(width='auto'))
TwoDanimOutput = widgets.Output()

def TwoDanim_Btn_clicked(a):
    anim = TwoDsnapAnim(TwoDanimRange.value[0],TwoDanimRange.value[1])
    TwoDanimOutput.clear_output()
    with TwoDanimOutput:
        display(HTML(anim.to_html5_video()))
TwoDanimBtn.on_click(TwoDanim_Btn_clicked)
TwoDanimBox = Box([Label(value='Surface Elevation animation'), TwoDanimRange, TwoDanimBtn], 
                  layout = Layout(width = '80%', justify_content = 'space-between'))


basicAnimBox = Box([depthBox, depthOutput,depProfileBox, TwoDsnapBox, TwoDanimBox, TwoDanimOutput, basicBox, basicOutput],
                   layout = Layout(flex_flow = 'column', align_items='stretch',))



rotatingBtn = Button(description='display',button_style='primary', layout=Layout(width='auto'))
rotatingOutput = widgets.Output()

def rotating_Btn_clicked(a):
    frames = []
    for i in range(1,surfaceFrame.max):
#         frames += [np.genfromtxt("output/output/eta_%05d" % i)]
        frames += [np.genfromtxt("output/f1/eta_%05d" % i)]
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



################################ Finally ##########################################################
        
tab_nest = widgets.Tab()
tab_nest.children = [SwanInputBox, runBox, outputBox, swanVisuAcd]
tab_nest.set_title(0, 'Input')
tab_nest.set_title(1, 'Run')
tab_nest.set_title(2, 'Output')
tab_nest.set_title(3, 'Visualization')

setvar("""PATH=$HOME/agave-model/bin:$PATH""")
cmd("auth-tokens-refresh")
clear_output()

def on_change(change):
    if(modelTitle.value == "SWAN"):
        out.clear_output()
        with out:
            tab_nest.children = [SwanInputBox, runBox, outputBox, swanVisuAcd]
            display(tab_nest)
    if(modelTitle.value == "Funwave-tvd"):
        out.clear_output()
        with out:
            tab_nest.children = [fwInputBox, runBox, outputBox, fwVisuAcd]
            display(tab_nest)
    if(modelTitle.value == "Delft3D"):
        out.clear_output()
        with out:
            tab_nest.children = [delft3dBox, runBox, outputBox, swanVisuAcd]
            display(tab_nest)
           
    
modelTitle.observe(on_change)


display(modelTitle)

out = widgets.Output()

with out:
    display(tab_nest)
display(out)

