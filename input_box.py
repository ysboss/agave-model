import os, re
import imp
from safe_reader import safe_reader
from ipywidgets import interactive, Layout, Button, Box, HBox, VBox, Text, Dropdown, Label, IntSlider, Textarea, Accordion, ToggleButton, ToggleButtons, Select, HTMLMath, FloatRangeSlider, Output, Tab, Checkbox, HTML
from logOp import *

if 'input_params' in globals():
    imp.reload(input_params)
else:
    import input_params

import pprint
pp = pprint.PrettyPrinter()

menus = {}
def get_tabs():
        global menus
        tabs = ["Choose Input Template"]
        cur_model = input_params.get('title').lower()
        menus[cur_model] = {}
        dir = "input_"+cur_model
        if not os.path.exists(dir):
            print("Path does not exist:",dir)
            return tuple(tabs)
        for f in os.listdir(dir):
            if re.match(r'\.',f):
                continue
            if not re.search(r'_template',f):
                continue
            fn = "input_"+cur_model+"/"+f
            with safe_reader(fn) as fr:
                found = False
                for line in fr.readlines():
                    g = re.search(r'\bmenu:\s*(.*\S)\s*->\s*(.*\S)',line)
                    if g:
                        label = g.group(1)
                        menus[cur_model][label] = {}
                        menus[cur_model][label]["outfile"] = g.group(2)
                        menus[cur_model][label]["infile"] = f
                        found = True
                        break
            if not found:
                label = f
                menus[cur_model][label] = {}
                menus[cur_model][label]["outfile"] = re.sub(r'_template','',f)
                menus[cur_model][label]["infile"] = f
            tabs += [label]
        return tuple(tabs)

def parseTemplateFile(templateFile):
    data = {}
    with safe_reader(templateFile) as fd:
        text = fd.read()
    for tagInfo in re.finditer(r'\${([^}]*)}',text):
        tag = tagInfo.group(1)
        item = {}
        for match in re.finditer(r'(\w+)=("[^"]*"|\'[^\']*\'|[^,\n]*)', tag):
            name = match.group(1)
            val = match.group(2)
            if val[0] == '"' and val[-1] == '"':
                val = val[1:-1]
            elif val[0] == "'" and val[-1] == "'":
                val = val[1:-1]
            if name == "label":
                data[val] = item
            else:
                item[name] = val
            item["_info_"] = tagInfo
    return text, data

def generatePara(templateFile):
    text, data = parseTemplateFile(templateFile)
    items = []
    for name in data.keys():
        val = data[name]
        if "option" in val:
            ops = val["option"].split('/')
            if "value" in val:
                label_value = val["value"]
            else:
                label_value = ops[0]
            label = Label(value = name, layout = Layout(width = "150px"))
            togBtns = ToggleButtons(options = ops)
            box = Box([label, togBtns], layout = Layout(width = '100%', justify_content = 'flex-start'))
            items.append(box)
        else:
            label_value = val["value"]
            label = Label(value = name, layout = Layout(width = "150px"))
            text = Text(value = label_value)
            box = Box([label, text], layout = Layout(width = '100%', justify_content = 'flex-start'))
            items.append(box)
    return items

def updatePara(templateFile, newInput, inputBox):
    text, data = parseTemplateFile(templateFile)
    pos = 0
    count = -1
    with open(newInput, "w") as fw:
        for name in data:
            count += 1
            datum = data[name]
            match = datum["_info_"]
            inputValue = inputBox.children[count].children[1].value
            print(text[pos:match.start()],sep='',end='',file=fw)
            print(inputValue,sep='',end='',file=fw)
            pos = match.end()
        print(text[pos:],sep='',end='',file=fw)
        log("Update file:", newInput)

class observe_template:
    def __init__(self,form,btn):
        self.form = form
        self.btn = btn
    def __call__(self,change):
        if change["name"] == "value":
            tabs = get_tabs()
            dd = change["owner"]
            if tabs != dd.options:
                dd.options = tabs
                dd.index = 0
            self.inputTmp = ''
            item = change["owner"]
            if item.index is not None:
                cur_model = input_params.get('title').lower()
                val = item.options[item.index]
                if val not in menus[cur_model]:
                    return
                self.inputTmp = 'input_' + cur_model + '/' + menus[cur_model][val]["infile"]
                self.outFile  = 'input_' + cur_model + '/' + menus[cur_model][val]["outfile"]
                self.form.children = generatePara(self.inputTmp)
                self.btn.description = 'Update Input File: '+self.outFile
                #updatePara(inputTmp,"/tmp/x.txt",self.form)
            else:
                self.inputTmp = None
                self.btn.description = 'Update Input File'

class save_input_file:
    def __init__(self,obj):
        self.obj = obj
    def __call__(self,button):
        if self.obj.inputTmp is not None:
            updatePara(self.obj.inputTmp,self.obj.outFile,self.obj.form)

class observe_title:
    def __init__(self, template_dropdown,clr):
        self.template_dropdown = template_dropdown
        self.clr = clr
    def __call__(self, change):
        if change["name"] == "value":
            tabs = get_tabs()
            dd = self.template_dropdown
            if tabs != dd.options:
                dd.options = tabs
                dd.index = 0
                self.clr()
