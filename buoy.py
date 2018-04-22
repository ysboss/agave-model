
import matplotlib.dates as mdates
from matplotlib.dates import date2num
import time
from datetime import datetime
import datetime
from matplotlib import dates

class Buoytable(object):
    def __init__(self,filename):
        self.filename = filename
        fo = open(self.filename, "r+")
        self.time = []
        self.Depth = []
        self.X_Windv = []
        self.Y_Windv = []
        self.Hsig = []
        self.Dir = []
        self.RTpeak = []
        self.Period = []
        self.Tm01 = []
        self.Tm02= []
        self.PkDir = []
        self.datalines = fo.readlines()[7:]
        fo.close()
        for line in self.datalines:
            p = line.split()
            self.time.append(p[0])
            self.Depth.append(p[3])
            self.X_Windv.append(p[4])
            self.Y_Windv.append(p[5])
            self.Hsig.append(p[6])
            self.Dir.append(p[7])
            self.RTpeak.append(p[8])
            self.Period.append(p[9])
            self.Tm01.append(p[10])
            self.Tm02.append(p[11])
            self.PkDir.append(p[12])
            
    def get_Time(self, index):
        gauge_time = []
        selectedtime = []
        for itime in range(int(index), len(self.datalines), 10):
            xx = self.time[int(itime)]
            ymd = xx[0:8]
            hms = xx[9:15]
            dt = time.mktime(datetime.datetime.strptime(ymd + hms, '%Y%m%d%H%M%S').timetuple())
            selectedtime.append(int(dt))
            gauge_time.append(self.time[int(itime)])
        dts = list(map(datetime.datetime.fromtimestamp, selectedtime))
        fds = dates.date2num(dts)
        return fds
    
    def get_Depth(self,index):
        gauge_Depth = []
        for itime in range(int(index), len(self.datalines), 10):
            gauge_Depth.append(self.Depth[int(itime)])
        return gauge_Depth

    def get_X_Windv(self, a):
        gauge_X_Windv = []
        for itime in range(int(a), len(self.datalines), 10):
            gauge_X_Windv.append(self.X_Windv[int(itime)])
        return gauge_X_Windv

    def get_Y_Windv(self,index):
        gauge_Y_Windv = []
        for itime in range(int(index), len(self.datalines), 10):
            gauge_Y_Windv.append(self.Y_Windv[int(itime)])
        return gauge_Y_Windv

    def get_Hsig(self,index):
        gauge_Hsig = []
        for itime in range(int(index), len(self.datalines), 10):
            gauge_Hsig.append(self.Hsig[int(itime)])
        return gauge_Hsig


    def get_Dir(self,index):
        gauge_Dir = []
        for itime in range(int(index), len(self.datalines), 10):
            gauge_Dir.append(self.Dir[int(itime)])
        return gauge_Dir

    def get_RTpeak(self, index):
        gauge_RTpeak = []
        for itime in range(int(index), len(self.datalines), 10):
            gauge_RTpeak.append(self.RTpeak[int(itime)])
        return gauge_RTpeak

    def get_Period(self, index):
        gauge_Period = []
        for itime in range(int(index), len(self.datalines), 10):
            gauge_Period.append(self.Period[int(itime)])
        return gauge_Period

    def get_Tm01(self, index):
        gauge_Tm01 = []
        for itime in range(int(index), len(self.datalines), 10):
            gauge_Tm01.append(self.Tm01[int(itime)])
        return gauge_Tm01

    def get_Tm02(self, index):
        gauge_Tm02 = []
        for itime in range(int(index), len(self.datalines), 10):
            gauge_Tm02.append(self.Tm02[int(itime)])
        return gauge_Tm02

    def get_PkDir(self,index):
        gauge_PkDir = []
        for itime in range(int(index), len(self.datalines), 10):
            gauge_PkDir.append(self.PkDir[int(itime)])
        #print (gauge_PkDir[0])
        return gauge_PkDir


#Depth       X-Windv       Y-Windv         Hsig           Dir         
#RTpeak        Period        Tm01          Tm02          PkDir
class Buoytable_refra(object):
    def __init__(self,filename):
        self.filename = filename
        fo = open(self.filename, "r+")
        self.times = []
        self.Depth = []
        self.X_Windv = []
        self.Y_Windv = []
        self.Hsig = []
        self.Dir = []
        self.RTpeak = []
        self.Period = []
        self.Tm01 = []
        self.Tm02= []
        self.PkDir = []
        self.FSpr = []
        self.datalines = fo.readlines()[7:]
        fo.close()
        for line in self.datalines:
            p = line.split()
            self.Hsig.append(p[0])
            self.RTpeak.append(p[1])
            self.Tm01.append(p[2])
            self.Tm02.append(p[3])
            self.FSpr.append(p[4])
            
            
   
    def get_Hsig(self,index):
        gauge_Hsig = []
        for itime in range(int(index), len(self.datalines), 12):
            gauge_Hsig.append(self.Hsig[int(itime)])
        return gauge_Hsig


    def get_RTpeak(self, index):
        gauge_RTpeak = []
        for itime in range(int(index), len(self.datalines), 12):
            gauge_RTpeak.append(self.RTpeak[int(itime)])
        return gauge_RTpeak


    def get_Tm01(self, index):
        gauge_Tm01 = []
        for itime in range(int(index), len(self.datalines), 12):
            gauge_Tm01.append(self.Tm01[int(itime)])
        return gauge_Tm01

    def get_Tm02(self, index):
        gauge_Tm02 = []
        for itime in range(int(index), len(self.datalines), 12):
            gauge_Tm02.append(self.Tm02[int(itime)])
        return gauge_Tm02

    def get_FSpr(self,index):
        gauge_FSpr = []
        for itime in range(int(index), len(self.datalines), 12):
            gauge_FSpr.append(self.FSpr[int(itime)])
        #print (gauge_FSpr[0])
        return gauge_FSpr