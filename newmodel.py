import os, re
import numpy as np
import ipywidgets
from ipywidgets import interactive, Layout, Button, Box, HBox, VBox, Text, Dropdown, Label, IntSlider, Textarea, Accordion, ToggleButton, ToggleButtons, Select, HTMLMath, FloatRangeSlider, Tab, Checkbox, HTML, Output
from IPython.display import display, clear_output, HTML
import json
import traceback
import sys

from setvar import *
from command import cmd
from modInput import modInput
import logOp

from safe_reader import safe_reader

import jetlag_conf

if 'input_params' in globals():
    imp.reload(input_params)
else:
    import input_params

######################## Previous ############################################################

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

### Global Box

if 'global_box' in globals():
    imp.reload(global_box)
else:
    import global_box

modelTitle = Dropdown(
    options=['SWAN', 'Funwave_tvd','Delft3D', 'OpenFoam', 'Cactus', 'NHWAVE'],
    value=input_params.get('title','SWAN'))
modelTitle.observe(global_box.observe_title)
middleware = Dropdown(options=['Tapis', 'Agave'],value=input_params.get('middleware','Tapis'))
middleware.observe(global_box.observe_middleware)
modelVersion = Dropdown()
globalWidth = '80px'
modelBox = VBox([Box([Label(value="Model", layout = Layout(width = globalWidth)), modelTitle]), 
                 Box([Label(value="Version", layout = Layout(width = globalWidth)),modelVersion]),
                 Box([Label(value="Middleware", layout = Layout(width = globalWidth)),middleware]),
                 ])
globalBox = Box([modelBox], 
               layout = Layout(display = 'flex', flex_flow = 'row', justify_content = 'space-between', width = '100%'))
display(globalBox)

### End Global Box

### Tab Nest

#=== Input Box

if 'input_box' in globals():
    imp.reload(input_box)
else:
    import input_box

templateDD = Dropdown(options=input_box.get_tabs(), value='Choose Input Template')
templateInputBox = Box(layout = Layout(flex_flow = 'column'))
UpInputBtn = Button(description='Update Input File',button_style='primary', layout=Layout(width='100%'))
InputBox = Box([templateDD, templateInputBox, UpInputBtn], 
                 layout = Layout(flex_flow = 'column', align_items = 'center'))

#=== Run Box
run_item_layout = Layout(
    display = 'flex',
    flex_flow = 'row',
    justify_content = 'flex-start',
    width = '50%'
)
jobNameText = Text(value = 'myjob')
machines = Dropdown(options=jetlag_conf.machines_options)
queues = Dropdown()
numXSlider = IntSlider(value=0, min=1, max=16, step=1)
numYSlider = IntSlider(value=0, min=1, max=16, step=1)
numZSlider = IntSlider(value=0, min=1, max=16, step=1)
runBtn = Button(description='Run', button_style='primary', layout= Layout(width = '50px'))
runWidth = '350px'
run_items = [
    Box([Label(value="Job Name", layout = Layout(width = runWidth)), jobNameText], layout = run_item_layout),
    Box([Label(value="Machine", layout = Layout(width = runWidth)), machines], layout = run_item_layout),
    Box([Label(value="Queue", layout = Layout(width = runWidth)), queues], layout = run_item_layout),
    Box([Label(value="NX", layout = Layout(width = runWidth)), numXSlider], layout = run_item_layout),
    Box([Label(value="NY", layout=Layout(width = runWidth)), numYSlider], layout= run_item_layout),
    Box([Label(value="NZ", layout=Layout(width = runWidth)), numZSlider], layout= run_item_layout),
    Box([runBtn]),
]
runBox = VBox(run_items)

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
build_model = Label(value=modelTitle.value + " VERSION", layout = Layout(width = '350px'))

# TODO: Need a better way of specifying this.... maybe a yaml file?
modelDd = Dropdown(options=['Swan','Funwave_tvd','OpenFoam', 'NHWAVE'])
modelVersionDd = Dropdown(options = ['4120','4110AB'])
mpiDd = Dropdown(options = ['None','3.3','3.2', '3.1.4'])
h5Dd = Dropdown(options = ['None','1.10.5','1.10.4', '1.8.21'])
hypreDd = Dropdown(options = ['None','2.11.2', '2.10.1'])

#=== Build box
msgOut = Output()
boxWidth = '350px'
build_items = [
    Box([build_model, modelVersionDd], layout = build_item_layout),
    Box([Label(value="Build Machine", layout = Layout(width = boxWidth)), machines], layout = build_item_layout),
    Box([Label(value="Queue", layout = Layout(width = boxWidth)), queues], layout = build_item_layout),
    ipywidgets.HTML(value="<b><font color='OrangeRed'><font size='2.5'>Select Dependent Software</b>"), 
    Box([Label(value="MPICH", layout = Layout(width = boxWidth)), mpiDd], layout = build_item_layout),
    Box([Label(value="HDF5", layout = Layout(width = boxWidth)), h5Dd], layout = build_item_layout),
    Box([Label(value="HYPRE", layout = Layout(width = boxWidth)), hypreDd], layout = build_item_layout),
    Box([buildBtn]),
    Box([msgOut])
]

buildTab = VBox(build_items)

tab_nest = Tab()
tab_nest.children = [InputBox, runBox, outputBox, buildTab]
tab_nest.set_title(0, 'Input')
tab_nest.set_title(1, 'Run')
tab_nest.set_title(2, 'Output')
tab_nest.set_title(3, 'Build')
##### End Model

form = tab_nest.children[0].children[1]

def clear_input_form():
    UpInputBtn.description = 'Update Input File'
    form.children = []

ddo = input_box.observe_template(form=form, btn=UpInputBtn)
templateDD.observe(ddo)
modelTitle.observe(input_box.observe_title(templateDD,clr=clear_input_form))
UpInputBtn.on_click(input_box.save_input_file(obj=ddo))

display(tab_nest)
display(logOp.logOp)

### End Tab Nest Model
