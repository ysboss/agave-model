from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
from matplotlib import animation, rc
from IPython.display import HTML
    
opdir = "output/output/"
    
############################################### 1D #############################################

def fwOneD(Y_in_plots):
    if(Y_in_plots =='Choose one'):
        return
    plt.clf()
    plt.cla()
    plt.close()
    
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    fig.subplots_adjust(left=0.2, wspace=0.4, hspace=0.4)
    
    X = []
    y1 = []
    y2 = []
    y3 = []
    y4 = []

    
    for frame in range(151):
        y = np.loadtxt(opdir+Y_in_plots+'_%05d' % (frame+1))
        y1.append(y[0][0])
        y2.append(y[20][100])
        y3.append(y[50][250])
        y4.append(y[80][450])
        
    for i in range(151):
        time = '%.2f' % ((i)*0.2)
        X.append(time)

    unit =''
    if (Y_in_plots == 'eta'):
        unit = '(m)'
    else:
        unit = '(m/s)'
        
    ax1.plot(X, y1)
    ax1.set_title("Location 1")
    ax1.set_ylabel(Y_in_plots+" "+unit)

    ax2.plot(X, y2)
    ax2.set_title("Location 2")
    #ax2.set_ylabel("Elevation")

    ax3.plot(X, y3)
    ax3.set_title("Location 3")
    ax3.set_ylabel(Y_in_plots+" "+unit)
    ax3.set_xlabel("Time (s)")

    ax4.plot(X, y4)
    ax4.set_title("Location 4")
    ax4.set_xlabel("Time (s)")

    fig_size = []
    fig_size.append(15)
    fig_size.append(8)
    plt.rcParams["figure.figsize"] = fig_size
    
    plt.show()


############################################### 2D #############################################    
    
def waterDepth(Mglob, Nglob):
    # Generate X_file 
    # 1 2 3 4 ...... 600
    # 1 2 3 4 ...... 600
    # 1 2 3 4 ...... 600
    fileX = open(opdir+'X_file','w')
    for i in range(int(Nglob)):
        for j in range(int(Mglob)):
            fileX.write(str(j+1)+' ')
        fileX.write('\n')
    fileX.close()
    
    # Generate Y_file
    # 1 1 1 1 ...... 1
    # 2 2 2 2 ...... 2
    #  ...... 
    # 200 200 ...... 200
    fileY = open(opdir+'Y_file','w')    
    for i in range(int(Nglob)):
        for j in range(int(Mglob)):
            fileY.write(str(i+1)+' ')
        fileY.write('\n')
    fileY.close()

#     fig_size = []
#     fig_size.append(8)
#     fig_size.append(5)
#     plt.rcParams["figure.figsize"] = fig_size
    
    # Load X_file and Y_file and get real dimension
    X = np.loadtxt(opdir+'X_file')
    X_value = X*0.05
    Y = np.loadtxt(opdir+'Y_file')
    Y_value = Y*0.10
    
    # Load depth file
    Depth = np.loadtxt(opdir+'dep.out')
    depplot = plt.contourf(X_value, Y_value, Depth, 100)
    plt.title("Water depth (m)")
    plt.colorbar()
    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")
    plt.tight_layout()
    #plt4.savefig("water depth.png")
    #return plt
    plt.show()
    
def depProfile(N):
    if (N==0):
        return
    depthfile = open(opdir+'dep.out','r')
    depthdata = depthfile.readlines()[N-1]
    p = depthdata.split()

    # load depth data to dep_value
    dep_value = []
    for i in range(600):
        dep_value.append(-abs(float(p[i])))

    # create x_value
    x_value = []
    for i in range(600):
        x_value.append((i+1)*0.05)
    
    
    fig, ax = plt.subplots()
    ax.plot(x_value, dep_value, color = '#FFFF00')
    ax.fill_between(x_value,-1, dep_value, facecolor='#FFFF00')
    plt.xlabel("X (m)")
    plt.ylabel("Depth (m)")
    plt.title("Depth at N = "+str(N))
    plt.show()

    
    
def depProfileWithEta(depth, start, end, total_time, plot_intv, Mglob):
    # open depth file 
    depthfile = open(opdir+'dep.out','r')
    depthdata = depthfile.readlines()[int(depth)-1]
    p = depthdata.split()

    # load depth data to dep_value
    dep_value = []
    for i in range(int(Mglob)):
        dep_value.append(-abs(float(p[i])))

    # create x_value
    x_value = []
    for i in range(int(Mglob)):
        x_value.append((i+1)*0.05)
    
    #fig = plt.figure()
    fig, ax = plt.subplots()

# create etas that contains all of needing eta data
    etas = []
    length = int(float(total_time)/float(plot_intv))
    for i in range(length):
        etafile = open(opdir+'eta_%05d' % (i+1))
        etadata = etafile.readlines()[10]
        etap = etadata.split()
        eta_value = []
        for m in range(int(Mglob)):
            eta_value.append(float(etap[m]))
        etas.append(eta_value)
        etafile.close()

    # define animate function
    def animate(i):
        ax.clear()
        ax.plot(x_value, etas[i], color='#33FFFF')
        ax.plot(x_value, dep_value, color='#FFFF00')
        ax.fill_between(x_value,-1, etas[i], facecolor='#33FFFF')
        ax.fill_between(x_value,-1, dep_value, facecolor='#FFFF00')
        time = '%.2f' % ((i+1)*float(plot_intv))
        ax.set_title('Time = '+ time +' sec')
        #plt.ylim(-0.45,0.1)
        #plt.xlabel("X (m)")
        #plt.ylabel("Elevation (m)")
        plt.close()
        ax.set_xlabel("X (m)")
        ax.set_ylabel("Elevation (m)")
        ax.set_ylim(-0.45,0.1)
        
        return ax

    # make animate 
    anim = animation.FuncAnimation(fig, animate, np.arange(int(start/float(plot_intv)), int(end/float(plot_intv))),
                                   interval=200, blit=False)
    return anim
    
    
def twoDsnapAnim(start, end, plot_intv):
    fig = plt.figure()
    fig,ax = plt.subplots()
    X = np.loadtxt(opdir+'X_file')
    X_value = X*0.05
    Y = np.loadtxt(opdir+'Y_file')
    Y_value = Y*0.10
    
    fig_size = []
    fig_size.append(8)
    fig_size.append(5)
    plt.rcParams["figure.figsize"] = fig_size
    
    def animate(i):
        ax.clear()
        Eta = np.loadtxt(opdir+'eta_%05d' % (i+1))
        img = ax.contourf(X_value, Y_value, Eta, 100)
        plt.colorbar(img)
        plt.close()
        time = '%.2f' % ((i+1)*float(plot_intv))
        ax.set_title('Time = '+ time +' sec')
        ax.set_xlabel("X (m)")
        ax.set_ylabel("Y (m)")
        return ax

    # make animate 
    anim = animation.FuncAnimation(fig,animate,np.arange(int(start/float(plot_intv)), int(end/float(plot_intv))), 
                                   interval=200,blit=False)
    return anim
    
def twoDsnapPlot(frame):    
    if (frame == 0):
        return
    X = np.loadtxt(opdir+'X_file')
    X_value = X*0.05
    Y = np.loadtxt(opdir+'Y_file')
    Y_value = Y*0.10
    
    Eta = np.loadtxt(opdir+'eta_%05d' % (frame+1))
    etaplot = plt.contourf(X_value, Y_value, Eta, 100)
    time = (frame-1)*0.2
    plt.title("Surface elevation (m) at t = "+str(time))
    plt.colorbar()
    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")
    plt.tight_layout()
    plt.show()
    
    
def basicAnimation(frames):
    size = len(frames)
    
    fig2, ax = plt.subplots(figsize=(12,12))
    def animate1(i):
        ax.clear()
        pltres = plt.imshow(frames[i])
        return pltres,
    
    anim = animation.FuncAnimation(fig2, animate1, frames=size, interval=200, repeat=True)
    return anim

    
############################################### 3D #############################################    
    
def surfacePlot(frame):
    # SLURP IN THE DATA
    if (frame == 0):
        return
#     f = np.genfromtxt("output/output/eta_%05d" % frame)
    f = np.genfromtxt(opdir+'eta_%05d' % frame)
    xv = np.linspace(0,f.shape[1],f.shape[1])
    yv = np.linspace(0,f.shape[0],f.shape[0])
    x2,y2 = np.meshgrid(xv,yv)
    fig = plt.figure(figsize=(12,10))
    ax = fig.gca(projection='3d')
    ax.clear()
    # This is the viewing angle, theta and phi
    ax.view_init(20,60)
    # For more colormaps, see https://matplotlib.org/examples/color/colormaps_reference.html
    # The strides make the image really sharp. They slow down the rendering, however.
    surf = ax.plot_surface(x2, y2, f, cmap=cm.coolwarm,
                           linewidth=0, antialiased=False, rstride=1, cstride=1)
    fig.colorbar(surf)
    plt.show()
    
    
def rotatingAnimation(frames):
    size = len(frames)
    if (size == 0):
        return
#     f = np.genfromtxt("output/output/eta_%05d" % 1)
    f = np.genfromtxt(opdir+'eta_%05d' % 1)
    xv = np.linspace(0,f.shape[1],f.shape[1])
    yv = np.linspace(0,f.shape[0],f.shape[0])
    x2,y2 = np.meshgrid(xv,yv)
    
    fig3 = plt.figure(figsize=(12,10))
    ax = fig3.gca(projection='3d')
    zmin = np.min(frames[0])
    zmax = np.max(frames[0])
    for i in range(1,size):
        zmin = min(zmin,np.min(frames[i]))
        zmax = max(zmax,np.max(frames[i]))
    def animate2(i):
        ax.clear()
        # Change the viewing angle
        ax.view_init(20,i*6)
        ax.set_zlim(top=zmax,bottom=zmin)
        # Cycle through the frames
        f = frames[i % 10]
        # vmax and vmin control the color normalization
        surf = ax.plot_surface(x2, y2, f, cmap=cm.coolwarm,
                           linewidth=0, antialiased=False, vmax=zmax, vmin=zmin)
        return surf,
    
    anim = animation.FuncAnimation(fig3, animate2, frames=size, interval=200, repeat=True)
    return anim




    

    