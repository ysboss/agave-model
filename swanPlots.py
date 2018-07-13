from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
from matplotlib import animation, rc
from IPython.display import HTML

from buoy import Buoytable
from matplotlib import dates
import matplotlib.dates as mdates
from command import cmd
from numpy import NaN

opdir = "output/"

def oneDPlots(Y_axis):
    if(Y_axis =='Choose one'):
        return
    plt.clf()
    plt.cla()
    plt.close()
    with open(opdir+'INPUT') as input_file:
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
    with open(opdir+buoy_point) as file1:
        for line in file1:
                data = line.strip().split()
                fname_k = "%s,%s" % (data[0],data[1])
                key_list.append(fname_k)
    filelist = dict(zip(key_list,range(len(key_list))))
    
    fig_size = []
    fig_size.append(15)
    fig_size.append(8)
    plt.rcParams["figure.figsize"] = fig_size
    
    Buoytable1 = Buoytable(opdir+buoy_table)
    
    for igauge in range(1,11):
        axs=plt.subplot(5,2,int(igauge)) # the first subplot in the first figure
        if (Y_axis=='Hsig'):
            pts = axs.plot(Buoytable1.get_Time(igauge-1), Buoytable1.get_Hsig(igauge-1))
        if (Y_axis=='PkDir'):
            pts = axs.plot(Buoytable1.get_Time(igauge-1), Buoytable1.get_PkDir(igauge-1))
        if (Y_axis=='RTpeak'):
            pts = axs.plot(Buoytable1.get_Time(igauge-1), Buoytable1.get_RTpeak(igauge-1))
        if (Y_axis=='X_Windv'):
            pts = axs.plot(Buoytable1.get_Time(igauge-1), Buoytable1.get_X_Windv(igauge-1))
        if (Y_axis=='Y_Windv'):
            pts = axs.plot(Buoytable1.get_Time(igauge-1), Buoytable1.get_Y_Windv(igauge-1))
            
        if (int(igauge)<=8):
            plt.xticks([])
        if (int(igauge)>=9):
            plt.xlabel("Date m/d/y")
            axs.xaxis.set_major_locator(dates.DayLocator(interval=1))
            axs.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
            plt.xticks(rotation=45,fontsize=8)
        if (int(igauge)==1 or int(igauge)==3 or int(igauge)==5 or int(igauge)==7 or int(igauge)==9):
            if (Y_axis=='Hsig'):
                plt.ylabel(Y_axis+' (m)')
            if (Y_axis=='PkDir'):
                plt.ylabel(Y_axis+' (degr)')
            if (Y_axis=='RTpeak'):
                plt.ylabel(Y_axis+' (sec)')
            if (Y_axis=='X_Windv'):
                plt.ylabel(Y_axis+' (m/s)')
            if (Y_axis=='Y_Windv'):
                plt.ylabel(Y_axis+' (m/s)')
        plt.title('buoy %s' %(igauge),fontsize=8)
        plt.setp(pts, 'color', 'b', 'linewidth', 2.0)
    
    plt.show()
    

def hsPreprocess_btn_clicked(a):
    cmd("mkdir -p output/hsTmp")
    for m in range(120):
        hs_array_time2=[]
        for j in range(109):
            fo = open(opdir+'hs', "r+")
            datalines1 = fo.readlines()[9+j+231*m]
        
            p1 = datalines1.split()
            for i in range(1,152):
                hs_array_time2.append(p1[i])
            fo = open(opdir+'hs', "r+")
            datalines2 = fo.readlines()[122+j+231*m]
            p2 = datalines2.split()
            for i in range(1,31):
                hs_array_time2.append(p2[i])
        fo.close()
        hsfilename = opdir+'hsTmp/hs_'+str(m+1)
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

    
def twoDAnimate(Time_Step):
    
    if (Time_Step == 0): 
        return 
    
    fig3, ax2 = plt.subplots()
    
    ax2.clear()
    
    xy_grid = np.loadtxt(opdir+'b02.xy')
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
    
    hsfilename=opdir+'hsTmp/hs_'+str(Time_Step)
    
    hs_value = np.loadtxt(hsfilename)
    hs_2d = np.reshape(hs_value,(109,181))
    hs_2d_final = hs_2d*0.01
    plt.contourf(longitude,latitude,hs_2d_final,30)
    plt.colorbar()
    #plt.colorbar(ticks=[0,0.5,1,1.5,2])
    plt.title("Hs (m)")
    plt.ylabel("latitude($^\circ$)")
    plt.xlabel("longitude($^\circ$)")
    plt.xlim(-98,-60)
    plt.ylim(7,47)
    plt.show()


