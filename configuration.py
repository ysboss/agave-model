from agave import *
from ipywidgets import Box, Text, Layout, Label, Button

readpass("MACHINE_PASSWD")
readpass("AGAVE_PASSWD")
readpass("PBTOK")

item_layout = Layout(
    display = 'flex',
    flex_flow = 'row',
    justify_content = 'flex-start',
    width = '50%'
)

agaveText = Text()
machineText = Text()
baseappText = Text()
machineNameText = Text()
confBtn = Button(description='Configure', layout= Layout(
    display = 'flex',
    flex_flow = 'row',
    justify_content = 'center',
    width = '100px',
    disabled=False
))

def confBtn_click(a):
    configure(agaveText.value, machineText.value, machineName.value, baseappText.value)

confBtn.on_click(confBtn_click)

items = [
    Box([Label(value='Agave username', layout = Layout(width = '120px')), agaveText], layout = item_layout),
    Box([Label(value='Machine username', layout = Layout(width = '120px')), machineText], layout = item_layout),
    Box([Label(value='Machine name', layout = Layout(width = '120px')), machineNameText], layout = item_layout),
    Box([Label(value='Project name', layout = Layout(width = '120px')), baseappText], layout = item_layout),
    Box([confBtn])
]

conf = Box(items, layout= Layout(
 #   display = 'flex',
    flex_flow = 'column',
    align_items='stretch',
    disabled=False))
display(conf)
