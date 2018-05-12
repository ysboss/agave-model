from __future__ import print_function
from ipywidgets import interact, interactive, fixed, interact_manual, Layout, Button, Box, FloatText, Text, Dropdown, Label, IntSlider, Textarea, Accordion, ToggleButton, ToggleButtons, Select
import ipywidgets as widgets
from IPython.display import display, clear_output
#from pylab import *
import matplotlib.pyplot as plt2
import sys
import numpy as np
from numpy import NaN
import os
import re
from upload import _upload_widget, setInput, _upload

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import date2num
import time
from datetime import datetime
import datetime
from matplotlib import dates

from agave import *
from setvar import *

from shutil import copyfile

from buoy import Buoytable

from command import cmd

######################## Input tab ############################################################
Time = ""

input_item_layout = Layout(
    display = 'flex',
    flex_flow = 'row',
    justify_content = 'flex-start',
    width = '50%'
)
  

modelTitle = Dropdown(options=['SWAN', 'Funwave-tvd','Delft3D'])
modelBox = Box([Label(value='Model', layout = Layout(width = '100px')), modelTitle], layout = input_item_layout)


    


######################## Input tab ############################################################
Time = ""

  
togBtns = ToggleButtons(options=['0.5', '1', '2'],
    description='',
    disabled=False,)

togBtn1 = ToggleButton(value = False, description = 'TIME')
togBtn2 = ToggleButton(value = False, description = 'XP')
togBtn3 = ToggleButton(value = False, description = 'YP')
togBtn4 = ToggleButton(value = False, description = 'DEP')
togBtn5 = ToggleButton(value = False, description = 'WIND')
togBtn6 = ToggleButton(value = False, description = 'HS')
togBtn7 = ToggleButton(value = False, description = 'DIR')
togBtn8 = ToggleButton(value = False, description = 'RTP')
togBtn9 = ToggleButton(value = False, description = 'PER')
togBtn10 = ToggleButton(value = False, description = 'TM01')
togBtn11 = ToggleButton(value = False, description = 'TM02')
togBtn12 = ToggleButton(value = False, description = 'PDIR')
togBtn13 = ToggleButton(value = False, description = 'Select Main Parameters', button_style = 'success')

togBtn14 = ToggleButton(value = False, description = 'sp1d')
togBtn15 = ToggleButton(value = False, description = 'sp2d')

togBtn16 = ToggleButton(value = False, description = 'wind')
togBtn17 = ToggleButton(value = False, description = 'hs')
togBtn18 = ToggleButton(value = False, description = 'dir')
togBtn19 = ToggleButton(value = False, description = 'per')



tabBox = Box([Label(value='Table', layout = Layout(width = '280px')),togBtn1,togBtn2,togBtn3,
              togBtn4,togBtn5,togBtn6,togBtn7,togBtn8,togBtn9,togBtn10,togBtn11,togBtn12], Layout = input_item_layout)
togBtnsBox = Box([Label(value='Time Step (h)', layout = Layout(width = '100px')),togBtns],Layout = input_item_layout )
specBox = Box([Label(value = 'Spectral Output', layout = Layout(width = '100px')), 
               togBtn14, togBtn15], Layout = input_item_layout)

blocBox = Box([Label(value = 'Block Output', layout = Layout(width = '100px')), 
               togBtn16, togBtn17, togBtn18, togBtn19], Layout = input_item_layout)

loadInputBtn =  Button(description='Load Input', layout= Layout(
    display = 'flex',
    flex_flow = 'row',
    justify_content = 'center',
    width = '20%',
    disabled=False
))

uploadInputBtn = Button(description='upload', layout= Layout(
    display = 'flex',
    flex_flow = 'row',
    justify_content = 'center',
    #width = '15%',
    disabled=False
))

saveInputBtn = Button(description='Update Input', layout= Layout(
    display = 'flex',
    flex_flow = 'row',
    justify_content = 'center',
    #width = '20%',
    disabled=False
))

inputArea = Textarea(layout= Layout(
    display = 'flex',
    flex_flow = 'row',
    justify_content = 'center',
    width = '70%',
    disabled=False
))

inputText = Text()
setInput(inputText)

modelTitle = Dropdown(options=['SWAN', 'Funwave-tvd','Delft3D'])

input_items = [
    Box([Label(value='Model', layout = Layout(width = '100px')), modelTitle], layout = input_item_layout),
    Box([Label(value='Upload File', layout = Layout(width = '125px')), inputText,_upload_widget], layout = input_item_layout),
    togBtnsBox,
    tabBox,
    specBox,
    blocBox,
    togBtn13,
    inputArea,
    saveInputBtn
]

def uploadInput_Btn_clicked(a):
    #os.system("mkdir -p input")
    #rcmd = "cp -a "+inputText.value+"/. input/"
    #cmd(rcmd)
    _upload()

uploadInputBtn.on_click(uploadInput_Btn_clicked)

def selectall_tBtn_clicked(a):
    if (togBtn13.value == True):
        togBtn1.value = True
        togBtn2.value = True
        togBtn3.value = True
        togBtn4.value = True
        togBtn5.value = True
        togBtn6.value = True
        togBtn7.value = True
        togBtn8.value = True
        togBtn9.value = True
        togBtn10.value = True
        togBtn11.value = True
        togBtn12.value = True
        togBtn14.value = True
        togBtn15.value = True
        togBtn16.value = True
        togBtn17.value = True
        togBtn18.value = True
        togBtn19.value = True
    else:
        togBtn1.value = False
        togBtn2.value = False
        togBtn3.value = False
        togBtn4.value = False
        togBtn5.value = False
        togBtn6.value = False
        togBtn7.value = False
        togBtn8.value = False
        togBtn9.value = False
        togBtn10.value = False
        togBtn11.value = False
        togBtn12.value = False
        togBtn14.value = False
        togBtn15.value = False
        togBtn16.value = False
        togBtn17.value = False
        togBtn18.value = False
        togBtn19.value = False
        
togBtn13.observe(selectall_tBtn_clicked, 'value')
    
def loadInput_Btn_clicked(a):
    inputArea.value = open('input/INPUT','r').read()

loadInputBtn.on_click(loadInput_Btn_clicked)

def judgeBtn(tb, value):
    if (tb.value == True):
        label = value;
    else:
        label = "";
    return label

def saveInput_Btn_clicked(a):
    #with open('input/INPUT','w') as output:
    #    output.write(inputArea.value)
    #cmd = "sed -i -e 's/TABLE/TABLE 234 "+togBtn1.description+"' INPUTtmp"
    #print (togBtn1.value)
    
    tb1_value = judgeBtn(togBtn1, "TIME")
    tb2_value = judgeBtn(togBtn2, "XP")
    tb3_value = judgeBtn(togBtn3, "YP")
    tb4_value = judgeBtn(togBtn4, "DEP")
    tb5_value = judgeBtn(togBtn5, "WIND")
    tb6_value = judgeBtn(togBtn6, "HS")
    tb7_value = judgeBtn(togBtn7, "DIR")
    tb8_value = judgeBtn(togBtn8, "RTP")
    tb9_value = judgeBtn(togBtn9, "PER")
    tb10_value = judgeBtn(togBtn10, "TM01")
    tb11_value = judgeBtn(togBtn11, "TM02")
    tb12_value = judgeBtn(togBtn12, "PDIR")
        
    rcmd = "TABLE  'BUOYS' HEAD  'buoy.tab' "+tb1_value+" "+tb2_value+" "+tb3_value+" "+tb4_value+" "+tb5_value+" "+tb6_value+" "+ tb7_value+" "+tb8_value+" "+tb9_value+" "+tb10_value+" "+tb11_value+" "+tb12_value+" OUT 20120826.000000 "+togBtns.value+" HR"

    with open("tmp","w") as tmp:
        f = open("input/INPUT","r+")
        index = 0;
        lines = f.readlines()
        for line in lines:
            if (index == 36):
                tmp.write(rcmd+'\n')
            elif (index == 37):
                if(togBtn14.value==True):
                    tmp.write("SPEC 'BUOYS' SPEC1D ABS 'buoy_sp1d' OUT 20120826.000000 "+togBtns.value+" HR\n")
                else:
                    tmp.write("$SPEC 'BUOYS' SPEC1D ABS 'buoy_sp1d' OUT 20120826.000000 "+togBtns.value+" HR\n")
            elif (index == 38):
                if(togBtn15.value==True):
                    tmp.write("SPEC 'BUOYS' SPEC1D ABS 'buoy_sp2d' OUT 20120826.000000 "+togBtns.value+" HR\n")
                else:
                    tmp.write("$SPEC 'BUOYS' SPEC1D ABS 'buoy_sp2d' OUT 20120826.000000 "+togBtns.value+" HR\n")
            elif (index == 39):
                if(togBtn16.value==True):
                    tmp.write("BLOCK 'COMPGRID' HEADER 'wind' LAY 4 WIND OUT 20050919.000000 "+togBtns.value+" HR\n")
                else:
                    tmp.write("$BLOCK 'COMPGRID' HEADER 'wind' LAY 4 WIND OUT 20050919.000000 "+togBtns.value+" HR\n")
            elif (index == 40):
                if(togBtn17.value==True):
                    tmp.write("BLOCK 'COMPGRID' HEADER 'hs' LAY 4 HS OUT 20050919.000000 "+togBtns.value+" HR\n")
                else:
                    tmp.write("$BLOCK 'COMPGRID' HEADER 'hs' LAY 4 HS OUT 20050919.000000 "+togBtns.value+" HR\n")
            elif (index == 41):
                if(togBtn18.value==True):
                    tmp.write("BLOCK 'COMPGRID' HEADER 'dir' LAY 4 DIR OUT 20050919.000000 "+togBtns.value+" HR\n")
                else:
                    tmp.write("$BLOCK 'COMPGRID' HEADER 'dir' LAY 4 DIR OUT 20050919.000000 "+togBtns.value+" HR\n")
            elif (index == 42):
                if(togBtn19.value==True):
                    tmp.write("BLOCK 'COMPGRID' HEADER 'per' LAY 4 PER OUT 20050919.000000 "+togBtns.value+" HR\n")
                else:
                    tmp.write("$BLOCK 'COMPGRID' HEADER 'per' LAY 4 PER OUT 20050919.000000 "+togBtns.value+" HR\n")
            elif (index == 45):
                tmp.write("COMPUTE NONST  20120826.000000 "+togBtns.value+" HR 20120826.020000\n")
            else:
                tmp.write(line)
            index+=1
    
    copyfile("tmp","input/INPUT")
    
    inputArea.value = open('input/INPUT','r').read()
    
saveInputBtn.on_click(saveInput_Btn_clicked)

inputBox = Box(input_items, layout= Layout(
 #   display = 'flex',
    flex_flow = 'column',
    align_items='stretch',
    disabled=False
))







funtogBtns = ToggleButtons(options=['5', '10', '20'],
    description='',
    disabled=False)
funtogBtnsBox = Box([Label(value='Time Step (h)', layout = Layout(width = '100px')),funtogBtns],Layout = input_item_layout )
                           
                           
funwave_items=[
    modelBox,
    funtogBtnsBox
]                        

funBox = Box(funwave_items, layout= Layout(
 #   display = 'flex',
    flex_flow = 'column',
    align_items='stretch',
    disabled=False
))




##################################### Run tab ################################
run_item_layout = Layout(
    display = 'flex',
    flex_flow = 'row',
    justify_content = 'flex-start',
    width = '50%'
)


runBtn = Button(description='Run SWAN', layout= Layout(
    display = 'flex',
    flex_flow = 'row',
    justify_content = 'center',
    width = '253px',
    disabled=False
))

abortBtn = Button(
    description='Abort',button_style='danger',  layout= Layout(
    display = 'flex',
    flex_flow = 'row',
    justify_content = 'center',
    width = '50',
    disabled=False
))

def runfun_btn_clicked(a):
    
    if (modelTitle.value == "SWAN"): 
        cmd("tar cvzf input.tgz input")
        cmd("files-upload -F input.tgz -S ${STORAGE_MACHINE} ${DEPLOYMENT_PATH}/")
        submitJob(numnodeSlider.value,numprocSlider.value) 
    
runBtn.on_click(runfun_btn_clicked)

def abort_btn_clicked(a):
    os.system('sudo pkill swan.exe')

abortBtn.on_click(abort_btn_clicked)

machineText = Text()
baseappText = Text()

numnodeSlider = IntSlider(value=0, min=1, max=8, step=1)
numprocSlider = IntSlider(value=0, min=1, max=16, step=1)

run_items = [
    
    #Box([Label(value='Agave password', layout = Layout(width = '120px')), agavePwText], layout = run_item_layout),
    Box([Label(value='Nodes', layout = Layout(width = '120px')), numnodeSlider], layout = run_item_layout),
    #Box([Label(value='Machine password', layout = Layout(width = '120px')), machinePwText], layout = run_item_layout),
    #Box([Label(value='Pushbullet token', layout = Layout(width = '120px')), PbtokText], layout = run_item_layout),
    #Box([Label(value='BaseApp name', layout = Layout(width = '120px')), baseappText], layout = run_item_layout),
    
    Box([Label(value='Processors', layout=Layout(width = '120px')), numprocSlider], layout= run_item_layout),
    Box([runBtn,abortBtn]),
]

runBox = Box(run_items, layout= Layout(
 #   display = 'flex',
    flex_flow = 'column',
    align_items='stretch',
    disabled=False
))










################################# Output tab ###################################
jobListBtn = Button(description='List jobs history', layout= Layout(
    display = 'flex',
    flex_flow = 'row',
    justify_content = 'center',
    width = '15%',
    disabled=False
))

jobSelect = Select(
    description='jobs history:',
    disabled=False,
    layout = Layout(width='60%')
)

jobOutputBtn = Button(description='List job output', layout= Layout(
    display = 'flex',
    flex_flow = 'row',
    justify_content = 'center',
    width = '15%',
    disabled=False
))

outputSelect = Select(
    description='job output:',
    disabled=False,
    layout = Layout(width='60%')
)

downloadOpBtn = Button(description='Get selected ouput', layout= Layout(
    display = 'flex',
    flex_flow = 'row',
    justify_content = 'center',
    width = '15%',
    disabled=False
))

def jobList_btn_clicked(a):
    cout = cmd("jobs-list -l 10")
    out1 = cout["stdout"]
    jobSelect.options = out1
    
jobListBtn.on_click(jobList_btn_clicked)


def jobOutput_btn_clicked(a):
    jobid = jobSelect.value[:-9] 
    rcmd = "jobs-output-list "+jobid
    cout = cmd(rcmd)
    out1 = cout["stdout"]
    outputSelect.options = out1
    
jobOutputBtn.on_click(jobOutput_btn_clicked)

def download_btn_clicked(a):
    try:
        jobid = jobSelect.value[:-9] 
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
    Box([jobSelect]),
    Box([jobOutputBtn]),
    Box([outputSelect]),
    Box([downloadOpBtn])
]



outputBox = Box(output_items, layout= Layout(
 #   display = 'flex',
    flex_flow = 'column',
    align_items='stretch',
    disabled=False
))



##################################### Show 1D tab ########################################
def showPlots(index):
    if(Yoption.value=='Choose one'):
        return
    plt.clf()
    plt.cla()
    plt.close()
    with open("output/INPUT") as input_file:
        for line in input_file:
            if line.startswith("$"):
                continue
            else:
                data = line.strip().split()
                if line.startswith("POINTS"):
                    buoy_point = "%s" % (data[3].strip('\''))
                elif line.startswith("TABLE"):
                    buoy_table = "%s" % (data[3].strip('\''))
                else:
                    continue
    input_file.close()
    key_list=[]
    with open("output/"+buoy_point) as file1:
        for line in file1:
                data = line.strip().split()
                fname_k = "%s,%s" % (data[0],data[1])
                key_list.append(fname_k)
    filelist = dict(zip(key_list,range(len(key_list))))
    
    fig_size = []
    fig_size.append(15)
    fig_size.append(8)
    plt.rcParams["figure.figsize"] = fig_size
    
    Buoytable1 = Buoytable("output/"+buoy_table)
    
    for igauge in range(1,11):
        axs=plt.subplot(5,2,int(igauge)) # the first subplot in the first figure
        if (Yoption.value=='Hsig'):
            pts = axs.plot(Buoytable1.get_Time(igauge-1), Buoytable1.get_Hsig(igauge-1))
        if (Yoption.value=='PkDir'):
            pts = axs.plot(Buoytable1.get_Time(igauge-1), Buoytable1.get_PkDir(igauge-1))
        if (Yoption.value=='RTpeak'):
            pts = axs.plot(Buoytable1.get_Time(igauge-1), Buoytable1.get_RTpeak(igauge-1))
        if (Yoption.value=='X_Windv'):
            pts = axs.plot(Buoytable1.get_Time(igauge-1), Buoytable1.get_X_Windv(igauge-1))
        if (Yoption.value=='Y_Windv'):
            pts = axs.plot(Buoytable1.get_Time(igauge-1), Buoytable1.get_Y_Windv(igauge-1))
            
        #pts = axs.plot(Buoytable1.get_Time(igauge-1), Buoytable1.get_X_Windv(igauge-1))
        if (int(igauge)<=8):
            plt.xticks([])
        if (int(igauge)>=9):
            plt.xlabel("Date m/d/y")
            axs.xaxis.set_major_locator(dates.DayLocator(interval=1))
            axs.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
            plt.xticks(rotation=45,fontsize=8)
        if (int(igauge)==1 or int(igauge)==3 or int(igauge)==5 or int(igauge)==7 or int(igauge)==9):
            if (Yoption.value=='Hsig'):
                plt.ylabel(Yoption.value+' (m)')
            if (Yoption.value=='PkDir'):
                plt.ylabel(Yoption.value+' (degr)')
            if (Yoption.value=='RTpeak'):
                plt.ylabel(Yoption.value+' (sec)')
            if (Yoption.value=='X_Windv'):
                plt.ylabel(Yoption.value+' (m/s)')
            if (Yoption.value=='Y_Windv'):
                plt.ylabel(Yoption.value+' (m/s)')
        plt.title('buoy %s' %(igauge),fontsize=8)
        plt.setp(pts, 'color', 'b', 'linewidth', 2.0)
    
    plt.show()
    
    
Yoption = Dropdown(options=['Choose one','Hsig','RTpeak','PkDir','X_Windv','Y_Windv'])
plotsInter = widgets.interactive(showPlots, index = Yoption )


Show1D_items = [plotsInter]
Show1DPlotsBox = Box(Show1D_items, layout= Layout(
 #   display = 'flex',
    flex_flow = 'column',
    align_items='stretch',
    disabled=False
))









############################### Show 2D tab ##########################################
fig3,ax2 = plt2.subplots()
def animate(index):
    
    if (hsIndex.value == 0): 
        return 
    
    ax2.clear()
    
    xy_grid = np.loadtxt('output/b02.xy')
    longitude = xy_grid[0:109]
    for i in range(109):
        for j in range(181):
            if(longitude[i][j]==(-999.0000000000)):
                longitude[i][j]= NaN
    latitude = xy_grid[109:218]
    for i in range(109):
        for j in range(181):
            if(latitude[i][j]==(-999.0000000000)):
                latitude[i][j]= NaN
    
    hsfilename='output/hsTmp/hs_'+str(index)
    
    hs_value = np.loadtxt(hsfilename)
    hs_2d = np.reshape(hs_value,(109,181))
    hs_2d_final = hs_2d*0.01
    plt2.contourf(longitude,latitude,hs_2d_final,30)
    plt2.colorbar()
    #plt.colorbar(ticks=[0,0.5,1,1.5,2])
    plt2.title("hs(m)")
    plt2.ylabel("latitude($^\circ$)")
    plt2.xlabel("longitude($^\circ$)")
    plt2.xlim(-110,-50)
    plt2.ylim(0,50)
    plt2.show()



hsIndex = IntSlider(value=0, min=0, max=120)
hsInter = widgets.interactive(animate, index = hsIndex)


hsPreprocessBtn = Button(description='HS Preprocess', layout= Layout(
    display = 'flex',
    flex_flow = 'row',
    justify_content = 'center',
    width = '403px',
    disabled=False
))

def hsPreprocess_btn_clicked(a):
    os.system("mkdir -p output/hsTmp")
    for m in range(120):
        hs_array_time2=[]
        for j in range(109):
            fo = open("output/hs", "r+")
            datalines1 = fo.readlines()[9+j+231*m]
        
            p1 = datalines1.split()
            for i in range(1,152):
                hs_array_time2.append(p1[i])
            fo = open("output/hs", "r+")
            datalines2 = fo.readlines()[122+j+231*m]
            p2 = datalines2.split()
            for i in range(1,31):
                hs_array_time2.append(p2[i])
        fo.close()
        hsfilename = 'output/hsTmp/hs_'+str(m+1)
        hs_file_object_time2 = open(hsfilename, 'w')
        for ip in hs_array_time2:
            if(ip=="-900."): 
                ip="NaN"
            hs_file_object_time2.write(ip)
            hs_file_object_time2.write('\n')
        hs_file_object_time2.close()

    fig_size = []
    fig_size.append(15)
    fig_size.append(8)

#showBtn.on_click(showPlot_btn_clicked)
hsPreprocessBtn.on_click(hsPreprocess_btn_clicked)

Show2D_items = [hsPreprocessBtn,hsInter]
Show2DPlotsBox = Box(Show2D_items, layout= Layout(
 #   display = 'flex',
    flex_flow = 'column',
    align_items='stretch',
    disabled=False
))





        
tab_nest = widgets.Tab()
tab_nest.children = [inputBox, runBox,outputBox, Show1DPlotsBox, Show2DPlotsBox]
tab_nest.set_title(0, 'Input')
tab_nest.set_title(1, 'Run')
tab_nest.set_title(2, 'Output')
tab_nest.set_title(3, 'Show 1D plots')
tab_nest.set_title(4, 'Show 2D plots')

setvar("""PATH=$HOME/swan/cli/bin:$PATH""")
cmd("auth-tokens-refresh")
clear_output()

def on_change(change):
    if(modelTitle.value == "SWAN"):
        tab_nest.children = [inputBox, runBox,outputBox, Show1DPlotsBox, Show2DPlotsBox]
        clear_output()
        display(tab_nest)
    if(modelTitle.value == "Funwave-tvd"):
        tab_nest.children = [funBox, runBox,outputBox, Show1DPlotsBox, Show2DPlotsBox]
        clear_output()
        display(tab_nest)

modelTitle.observe(on_change)


display(tab_nest)
