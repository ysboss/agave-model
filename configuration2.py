from agave import *
from ipywidgets import Box, Text, Layout, Label, Button

item_layout = Layout(
    display = 'flex',
    flex_flow = 'row',
    justify_content = 'flex-start',
    width = '50%'
)

agaveText = Text()
execMachineText = Text()
machineNameText = Text()
appText = Text()
pbtokText = Text()
confBtn = Button(description='Configure', layout= Layout(
    display = 'flex',
    flex_flow = 'row',
    justify_content = 'center',
    width = '100px',
    disabled=False
))

def confBtn_click(a):
    configure2(agaveText.value, execMachineText.value, machineNameText.value, appText.value)

confBtn.on_click(confBtn_click)

items = [
    Box([Label(value='Agave username', layout = Layout(width = '140px')), agaveText], layout = item_layout),
    Box([Label(value='Execute machine', layout = Layout(width = '140px')), execMachineText], layout = item_layout),
    Box([Label(value='Storage system name', layout = Layout(width = '140px')), machineNameText], layout = item_layout),
    Box([Label(value='Project name', layout = Layout(width = '140px')), appText], layout = item_layout),
    #Box([Label(value='PBTOK', layout = Layout(width = '140px')), pbtokText], layout = item_layout),
    Box([confBtn])
]

conf = Box(items, layout= Layout(
    flex_flow = 'column',
    align_items='stretch',
    disabled=False))
display(conf)
