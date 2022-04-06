from jetlag import RemoteJob
import os, re
import numpy as np
import ipywidgets
from ipywidgets import interactive, Layout, Button, Box, HBox, VBox, Text, Dropdown, Label, IntSlider, Textarea, Accordion, ToggleButton, ToggleButtons, Select, HTMLMath, FloatRangeSlider, Tab, Checkbox, HTML, Output, FileUpload
from IPython.display import display, clear_output, HTML
import json
import traceback
import sys
from write_env import write_env

from setvar import *
from command import cmd
from modInput import modInput

import input_params
import jetlag_conf
from safe_reader import safe_reader
from logOp import logOp, clearLog, log
from here import here

import pprint
pp = pprint.PrettyPrinter()

from model_versions import *

######################## Previous ############################################################

tab_nest = None

def decode_bytes(c):
    s = ''
    if type(c) == bytes:
        for k in c:
            s += chr(k)
        return s
    else:
        return c

def relink(dir_a, dir_b):
    for f in os.listdir(dir_a):
        fa = dir_a+"/"+f
        fb = dir_b+"/"+f
        if os.path.isdir(fa):
            os.makedirs(fb, exist_ok=True)
            relink(fa, fb)
        else:
            os.link(fa, fb)

def getJSONData(jsonData, title, ver):
    for json_dir in json_dirs:
        for f in os.listdir(json_dir):
            if not re.match(r'^.*-.*\.json$', f):
                continue
            p = os.path.join(json_dir, f)
            if os.path.isfile(p):
                with open(p,'r') as file:
                    jsonData = file.read()
    return jsonData            
#############################################

models, packages = getModelsAndPacks(False)

if len(models)>0:
    input_params.set('title', models[0])
input_params.set("last_jid", jetlag_conf.get_uv().jetlag_id)
if len(models) > 0 and len(packages) > 0:
    vers = get_versions(packSplit(packages[0]))
    if len(vers) > 0:
        input_params.set('modelversion_%s' % models[0].lower(), vers[0])
mpichOptions = get_versions("mpich")
hypreOptions = get_versions("hypre")
hdf5Options = get_versions("hdf5")
if len(mpichOptions)>0:
    input_params.set("mpich-ver", mpichOptions[0])
if len(hypreOptions)>0:
    input_params.set("hypre-ver", hypreOptions[0])
if len(hdf5Options)>0:
    input_params.set("hdf5-ver", hdf5Options[0])

jsonData = None
title = input_params.get('title','').lower()
ver = input_params.get('modelversion')

textBox = Textarea(
    value=getJSONData(jsonData, title, ver),
    placeholder='',
    rows = 1,
    #description= input_params.get('title').lower() +'@'+input_params.get('modelversion'),
    disabled=False,
    layout=Layout(width="auto", height="100%"))

##############################################
### Global Box

import global_box

#userName = Label(value=jetlag_conf.get_user())
model_value = input_params.get('title','SWAN')
if model_value in models:
    modelTitle = Dropdown(
        options=models,
        value=model_value)
else:
    modelTitle = Dropdown()
modelTitle.observe(global_box.observe_title)

middleware_value=jetlag_conf.get_uv().utype
input_params.set('middleware', middleware_value)
middleware = Label(value=middleware_value)
vers = get_versions(input_params.get('title'))
if len(vers) > 0:
    modelVersion = Dropdown(options=vers, value=vers[0])
else:
    modelVersion = Dropdown()

def update_version(c):
    if c["name"] == "value":
        input_params.set('modelversion', c["new"])
        mod = input_params.get('title')
        model = mod.lower()
        input_params.set('modelversion_%s' % model, c["new"])
        title = input_params.get('title').lower()
        ver = input_params.get('modelversion')
        jdata = getJSONData(jsonData, title, ver)
        if jdata is not None:
            textBox.value = jdata
              

modelVersion.observe(update_version)
input_params.set('modelversion', modelVersion.value)
globalWidth = '80px'
clearLogBtn = Button(description='Clear log', button_style='primary', layout = Layout(width = '115px'))
def clearLog_btn_clicked(a):
    clearLog()

clearLogBtn.on_click(clearLog_btn_clicked)
modelBox = VBox([
    #Box([Label(value="User", layout = Layout(width = globalWidth)), userName]),
                 clearLogBtn,
                 Box([Label(value="Model", layout = Layout(width = globalWidth)), modelTitle]), 
                 Box([Label(value="Version", layout = Layout(width = globalWidth)),modelVersion]),
                 ])
globalBox = Box([modelBox], 
               layout = Layout(display = 'flex', flex_flow = 'row', justify_content = 'space-between', width = '100%'))
display(globalBox)

### End Global Box

### Tab Nest

#=== Input Box

import input_box

templateDD = Dropdown(options=input_box.get_tabs(), value='Choose Input Template')
templateInputBox = Box(layout = Layout(flex_flow = 'column'))
UpInputBtn = Button(description='Update Input File',button_style='primary', layout=Layout(width='100%'))
UploadBtn = FileUpload(multiple=True)

def get_dname():
    model = value=input_params.get('title').lower()
    if model != "None":
        dname = f"{work_dir}/input_"+model
    return 'To upload via command line: docker cp [file] cmr:%s/' % dname
UploadLabel = Label(value=get_dname())

def update_label(change):
    global UploadLabel
    if change["name"] == "value":
        UploadLabel.value = get_dname()
        #textBox.decription = input_params.get('title').lower() +'@'+input_params.get('modelversion')
modelTitle.observe(update_label)

def update_name(change):
    global userName
    userName.value = jetlag_conf.get_user()

InputBox = Box([templateDD, templateInputBox, UpInputBtn, UploadBtn, UploadLabel], 
                 layout = Layout(flex_flow = 'column', align_items = 'center'))

if os.path.exists("%s/agave-model/input_none" % os.environ["HOME"]):
    os.system("rm -r %s/agave-model/input_none" % os.environ["HOME"])
    
#=== Run Box
run_item_layout = Layout(
    display = 'flex',
    flex_flow = 'row',
    justify_content = 'flex-start',
    width = '75%'
)
jobNameText = Text(value = input_params.get('jobname','myjob'))
def observe_job_name(change):
    if change["name"] == "value":
        input_params.set('jobname',change["new"])
jobNameText.observe(observe_job_name)

proc_str = input_params.get('NPROCS','1*1*1')
procs = []
for m in re.findall(r'\d+',proc_str):
    procs += [int(m)]
while len(procs) < 3:
    procs += [0]

numProcsText = Text(value = proc_str)

if len(jetlag_conf.machines_options) == 0:
    machinesValue = None
else:
    machinesValue = input_params.get('machine_'+middleware_value,jetlag_conf.machines_options[0])
if machinesValue is None:
    pass
elif machinesValue not in jetlag_conf.machines_options:
    machinesValue = jetlag_conf.machines_options[0]
machines = Dropdown(options=jetlag_conf.machines_options,value=machinesValue) 
def observe_machines(change):
    if change["name"] == "value":
        middleware_value=input_params.get('middleware')
        input_params.set('machine_'+middleware_value, change["new"])
machines.observe(observe_machines)

maxSlide = 128
numXSlider = IntSlider(value=procs[0], min=1, max=maxSlide, step=1)
numYSlider = IntSlider(value=procs[1], min=1, max=maxSlide, step=1)
numZSlider = IntSlider(value=procs[2], min=1, max=maxSlide, step=1)

disable_sliders = False
def observe_num_procs(change):
    global disable_sliders
    if change["name"] == "value":
        try:
            disable_sliders = True
            val = change["new"]
            i = 0
            changed = False
            for m in re.findall(r'\d+',val):
                i += 1
                mv = int(m)
                if i == 1:
                    if mv != numXSlider.value:
                        numXSlider.value = mv
                        changed = True
                elif i==2:
                    if mv != numYSlider.value:
                        numYSlider.value = mv
                        changed = True
                elif i==3:
                    if mv != numZSlider.value:
                        numZSlider.value = mv
                        changed = True
            if changed:
                input_params.set('NPROCS',val)
        finally:
            disable_sliders = False

def observe_n_change(change):
    if disable_sliders:
        return
    if change["name"] == "value" and change["old"] != change["new"]:
        val = "%d*%d*%d" % (numXSlider.value, numYSlider.value, numZSlider.value)
        if numProcsText.value != val:
            numProcsText.value = val
            input_params.set('NPROCS',val)

numProcsText.observe(observe_num_procs)
numXSlider.observe(observe_n_change)
numYSlider.observe(observe_n_change)
numZSlider.observe(observe_n_change)

import run_tab
runBtn = Button(description='Run', button_style='primary', layout= Layout(width = '50px'))
runWidth = '150px'
run_items = [
    Box([Label(value="Job Name", layout = Layout(width = runWidth)), jobNameText], layout = run_item_layout),
    #Box([Label(value="Machine", layout = Layout(width = runWidth)), machines], layout = run_item_layout),
    #Box([Label(value="Queue", layout = Layout(width = runWidth)), queues], layout = run_item_layout),
    Box([Label(value="NX", layout = Layout(width = runWidth)), numXSlider], layout = run_item_layout),
    Box([Label(value="NY", layout=Layout(width = runWidth)), numYSlider], layout= run_item_layout),
    Box([Label(value="NZ", layout=Layout(width = runWidth)), numZSlider], layout= run_item_layout),
    Box([Label(value="NX*NY*NZ", layout=Layout(width = runWidth)), numProcsText], layout= run_item_layout),
    Box([runBtn]),
]
runBox = VBox(run_items)
runBtn.on_click(run_tab.run)

#=== Output Box
jobListBtn = Button(description='List all jobs', button_style='primary', layout= Layout(width = '115px'))
jobSelect = Select(layout = Layout(height = '150px', width='100%'))

jobOutputBtn = Button(description='List job output', button_style='primary', layout= Layout(width = '115px'))
abortBtn = Button(description='Abort', button_style='danger', layout= Layout(width = 'auto'))
outputSelect = Select(layout = Layout(height = '150px', width='100%'))
downloadOpBtn = Button(description='Download', button_style='primary', layout= Layout(width = '115px'))
jobHisBtn = Button(description='Job history', button_style='primary', layout= Layout(width = '115px'))
jobHisSelect = Select(layout = Layout(height = '336px', width='100%'))

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
outputBox = HBox([
    VBox(output_items_left, layout = Layout(width='50%')),
    VBox(output_items_right, layout = Layout(width='50%'))],
    layout = Layout(width='100%'))
build_item_layout = Layout(
    display = 'flex',
    flex_flow = 'row',
    justify_content = 'flex-start',
    width = '50%'
)

buildBtn = Button(description = "Build", button_style='primary', layout= Layout(width = '50px'))
updateBtn = Button(description = "Update Models/Versions", button_style ='danger', layout=Layout(width = '200px'))
if modelTitle.value is not None:
    build_model = Label(value=modelTitle.value + " VERSION", layout = Layout(width = '350px'))
else:
    build_model = Label("???", layout = Layout(width = '350px'))

def build_model_observer(change):
    global build_model
    if change["name"] == "value":
        build_model.value = modelTitle.value + " VERSION"
modelTitle.observe(build_model_observer)

def abort_btn_clicked(a):
    g = re.match(r'^(\S+)\s+(\S+)\s+(\S+)',jobSelect.value)
    jobid = g.group(3)
    with logOp:
        if g:
            jobid = g.group(3)
            uv = jetlag_conf.get_uv()
            uv.job_stop(jobid)
            print("Job stopped:",jobid)

abortBtn.on_click(abort_btn_clicked)

def jobList_btn_clicked(a):
    with logOp:
        try:
            jobSelect.options = ["loading..."]
            out1 = []
            uv = jetlag_conf.get_uv()
            for j in uv.job_list(10):
                out1 += [j["status"]+" "+j["name"]+"  "+j["id"]]
            jobSelect.options = out1
            # Need to set to None first, otherwise it doesn't take
            jobSelect.index = None
            jobSelect.index = 0
        except Exception as e:
            jobSelect.options = ["error: "+str(e)]
            traceback.print_exc(file=sys.stdout)
    
jobListBtn.on_click(jobList_btn_clicked)

def jobOutput_btn_clicked(a):
    g = re.match(r'^(\S+)\s+(\S+)\s+(\S+)',jobSelect.value)
    with logOp:
        if g:
            jobid = g.group(3)
            uv = jetlag_conf.get_uv()
            outputSelect.options = ["loading..."]
            out1 = uv.job_file_list(jobid)
            outputSelect.options = out1
            if len(out1)==0:
                outputSelect.options = ["empty"]
        else:
            outputSelect.options = []
            print("pattern did not match:",jobSelect.value)

jobOutputBtn.on_click(jobOutput_btn_clicked)

def jobHis_btn_clicked(a):
    g = re.match(r'^(\S+)\s+(\S+)\s+(\S+)',jobSelect.value)
    with logOp:
        if g:
            jobid = g.group(3)
            print("History for job %s" % jobid)
            uv = jetlag_conf.get_uv()
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

def download_btn_clicked(a):
    with logOp:
        try:
            g = re.match(r'^(\S+)\s+(\S+)\s+(\S+)',jobSelect.value)
            if not g:
                print("No jobs")
                return
            jobid = g.group(3)
            uv = jetlag_conf.get_uv()
        
            if outputSelect.value == '/output.tgz':
                print("Downloading output tarball to jobdata-"+jobid)
                job = RemoteJob(uv, jobid)
                job.get_result()
                cmd("cp jobdata-%s/output.tgz ." % jobid)
                cmd("rm -fr run_dir")
                cmd("tar xzf output.tgz")
            elif re.match(r'.*\.(txt|out|err|ipcexe|log)',outputSelect.value):
                rcmd = uv.get_file(jobid,outputSelect.value)
                print(decode_bytes(rcmd))
            else:
                f1 = outputSelect.value
                f2 = re.sub(r'.*/','',f1)
                print("Download:",f1,"->",f2)
                rcmd = uv.get_file(jobid,f1,as_file=f2)
        except Exception as ex:
            with logOp:
                print("DIED!",ex)
                traceback.print_exc(file=sys.stdout)

downloadOpBtn.on_click(download_btn_clicked)


# TODO: Need a better way of specifying this.... maybe a yaml file?
modelDd = Dropdown(options=models)
modelVersionDd = Dropdown(options = get_versions(input_params.get('title')))
if len(mpichOptions)>0:
    mpiDd = Dropdown(options = mpichOptions,
        value=input_params.get('mpich-ver',mpichOptions[0]))
else:
    mpiDd = Dropdown()
if len(hdf5Options)>0:
    h5Dd = Dropdown(options = hdf5Options,
        value=input_params.get('hdf5-ver', hdf5Options[0]))
else:
    h5Dd = Dropdown()
if len(hypreOptions)>0:
    hypreDd = Dropdown(options = hypreOptions,
        value=input_params.get('hypre-ver',hypreOptions[0]))
else:
    hypreDd = Dropdown()

def save_mpich(change):
    if change['name'] == 'value':
        input_params.set('mpich-ver',change['new'])
mpiDd.observe(save_mpich)

def save_hdf5(change):
    if change['name'] == 'value':
        input_params.set('hdf5-ver',change['new'])
h5Dd.observe(save_mpich)

def save_hypre(change):
    if change['name'] == 'value':
        input_params.set('hypre-ver',change['new'])
hypreDd.observe(save_mpich)

enable_model_change = True
def save_model_change(change):
    if change['name'] == 'value' and enable_model_change:
        model = value=input_params.get('title').lower()
        model_key="modelversion_"+model
        input_params.set(model_key, change['new'])

modelVersionDd.observe(save_model_change)


def model_change(change):
    global enable_model_change
    if change['type'] == 'change' and change['name'] == 'value':
        if(change['new'] in models):
            index = models.index(change['new'])
            options = get_versions(packSplit(packages[index]))
        else:
            print("change:",change["new"])
            return
        try:
            enable_model_change = False
            modelVersionDd.options = options
            modelVersion.options = options
            model_key="modelversion_"+change["new"].lower()
            ver = input_params.get(model_key)
            if ver is None or ver == "None":
                for opt in options:
                    if opt is None or opt == "None":
                        continue
                    ver = opt
                    break
            if ver is None or ver == "None":
                return
            input_params.set(model_key,ver)
            try:
                modelVersionDd.value = ver
            except:
                with logOp:
                    print(f"Could not set {ver} for {change['new'].lower()}")
            try:
                modelVersion.value = ver
            except:
                with logOp:
                    print(f"Could not set {ver} for {change['new'].lower()}!")
        finally:
            enable_model_change = True

model_change({
    "name":"value",
    "type":"change",
    "new":input_params.get('title','')
})
modelTitle.observe(model_change)
box1 = VBox([textBox], layout={'height': '200px'})
box2 = HBox([updateBtn], layout=Layout(align_items='center'))
#=== Build box
#msgOut = Output()
#boxWidth = '350px

#Select(layout = Layout(height = '150px', width='50%'))
build_items = [
    #Box([build_model, modelVersionDd], layout = build_item_layout),
    #Box([Label(value="Build Machine", layout = Layout(width = boxWidth)), machines], layout = build_item_layout),
    #Box([Label(value="Queue", layout = Layout(width = boxWidth)), queues], layout = build_item_layout),
    #ipywidgets.HTML(value="<b><font color='OrangeRed'><font size='2.5'>Select Dependent Software</b>"), 
    #Box([Label(value="MPICH", layout = Layout(width = boxWidth)), mpiDd], layout = build_item_layout),
    #Box([Label(value="HDF5", layout = Layout(width = boxWidth)), h5Dd], layout = build_item_layout),
    #Box([Label(value="HYPRE", layout = Layout(width = boxWidth)), hypreDd], layout = build_item_layout),
    HBox([box1, box2], layout = Layout(justify_content="space-between", align_items='center'))
    #,
    #Box([msgOut])
]

# def versions_observe(change):
#     if change["name"] == "value":
#         input_params.set('mpich-ver',mpiDd.value)
#         input_params.set('hdf5-ver',h5Dd.value)
#         input_params.set('hypre-ver',hypreDd.value)

# mpiDd.observe(versions_observe)

# def do_build(btn):
#     with logOp:
#         cmd("rm -fr run_dir input.tgz")
#         cmd("mkdir -p run_dir")
#         with open("run_dir/runapp.sh","w") as fd:
#             print("singularity exec $SING_OPTS --pwd $PWD $IMAGE bash ./build.sh",file=fd)

#         files = ["build.sh"]
#         for fn in os.listdir("."):
#             if re.match(r'^build-.*\.sh$',fn):
#                 files += [fn]
#         write_env()
#         cmd("cp %s run_dir/" % " ".join(files))
#         cmd("tar czf input.tgz run_dir")
#         uv = jetlag_conf.get_uv()
#         uv.run_job('build',jtype='fork',nodes=1)
#         #cmd(uv.fill("scp -i uapp-key env.sh build.sh runbuild.sh {machine_user}@{machine}.{domain}:."))
#         #cmd(uv.fill("ssh -i uapp-key {machine_user}@{machine}.{domain} bash ./runbuild.sh"))

def update_vers(btn):
    
    models, packages = getModelsAndPacks(True)
        
    if os.path.exists("machineFiles/spack-info.txt"):
        print("Models and Versions Updated!")
        print("Please restart the CMR")
    else:
        print("Something went wrong with your attempt to configure the CMR")
        
#buildBtn.on_click(do_build)
updateBtn.on_click(update_vers)

buildTab = VBox(build_items)

tab_nest = Tab()
tab_nest.children = [InputBox, runBox, outputBox, buildTab]
tab_nest.set_title(0, 'Input')
tab_nest.set_title(1, 'Run')
tab_nest.set_title(2, 'Output')
tab_nest.set_title(3, 'Build')
tab_nest.selected_index = input_params.get('tabindex',0)
##### End Model

# Keep tab selection the same when the model is reloaded
def tab_observer(c):
    if c["name"] == "selected_index":
        input_params.set('tabindex',c["new"])

tab_nest.observe(tab_observer)

form = tab_nest.children[0].children[1]

def clear_input_form():
    UpInputBtn.description = 'Update Input File'
    form.children = []

ddo = input_box.observe_template(form=form, btn=UpInputBtn)
templateDD.observe(ddo)
modelTitle.observe(input_box.observe_title(templateDD,clr=clear_input_form))
UpInputBtn.on_click(input_box.save_input_file(obj=ddo))

display(tab_nest)
display(logOp)
clearLog()

from ipywidgets import FileUpload
import os
#upload = FileUpload(multiple=True)
class observe_file_upload:
    def __init__(self):
        self.metadata = None
        self.name = []

    def __call__(self,change):
        try:
            self.callme(change)
        except:
           with logOp:
              traceback.print_exc(file=sys.stdout)

    def callme(self, change):
            
        n = change["name"]
        v = change["new"]
        if n == "metadata":
            # Loops through each user uploaded
            # file in list "v" and appends its
            # file name as a string to list "name"
            for i in range(len(v)):
                self.metadata = v[i]
                self.name.append(self.metadata["name"])
        elif n == "data":
            for j in range(len(v)):
                d = v[j]
                assert type(d) == bytes
                #if re.match(r'^.*\.(zip|tgz|tar.gz)',self.name[j]):
                #    dname = os.path.join(os.environ["HOME"], "Download")
                #else:
                model = value=input_params.get('title').lower()
                dname = f"{work_dir}/input_"+model
                if re.match(r'^.*\.(zip|tgz|tar.gz)',self.name[j]):
                    with logOp:
                        cmd(['rm','-fr',dname],cwd=work_dir)
                os.makedirs(dname,exist_ok=True)
                fname = os.path.join(dname, self.name[j])
                with open(fname,"wb") as fd:
                    fd.write(d)
                if os.path.exists(fname):
                    log("upload of '",fname,"' was successful.",sep='')
                else:
                    log("upload of '",fname,"' failed.",sep='')
                with in_dir(dname):
                    with logOp:
                        if re.match(r'^.*\.(tgz|tar\.gz)$', self.name[j]):
                            cmd(['tar','xzf',self.name[j]])
                            cmd(['rm','-f',self.name[j]])
                        elif re.match(r'^.*\.(tar)$', self.name[j]):
                            cmd(['tar','xf',self.name[j]])
                            cmd(['rm','-f',self.name[j]])
                        elif re.match(r'^.*\.(zip)$', self.name[j]):
                            cmd(['unzip',self.name[j]])
                            cmd(['rm','-f',self.name[j]])
            self.metadata = None
            self.name = []

UploadBtn.observe(observe_file_upload())
