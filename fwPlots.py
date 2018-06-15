from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
from matplotlib import animation, rc
from IPython.display import HTML
    
def surfacePlot(frame):
    # SLURP IN THE DATA
    if (frame == 0):
        return
    f = np.genfromtxt("output/output/eta_%05d" % frame)
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
    


def basicAnimation(frames):
    size = len(frames)
    
    fig2, ax = plt.subplots(figsize=(12,12))
    def animate1(i):
        ax.clear()
        pltres = plt.imshow(frames[i])
        return pltres,
    
    anim = animation.FuncAnimation(fig2, animate1, frames=size, interval=200, repeat=True)
    return anim

    



def rotatingAnimation(frames):
    size = len(frames)
    if (size == 0):
        return
    f = np.genfromtxt("output/output/eta_%05d" % 1)
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
    
def waterDepth():
    # Generate X_file 
    # 1 2 3 4 ...... 600
    # 1 2 3 4 ...... 600
    # 1 2 3 4 ...... 600
    fileX = open('output/X_file','w')
    for i in range(200):
        for j in range(600):
            fileX.write(str(j+1)+' ')
        fileX.write('\n')
    fileX.close()
    
    # Generate Y_file
    # 1 1 1 1 ...... 1
    # 2 2 2 2 ...... 2
    #  ...... 
    # 200 200 ...... 200
    fileY = open('output/Y_file','w')    
    for i in range(200):
        for j in range(600):
            fileY.write(str(i+1)+' ')
        fileY.write('\n')
    fileY.close()

    # Load X_file and Y_file and get real dimension
    X = np.loadtxt('output/X_file')
    X_value = X*0.05
    Y = np.loadtxt('output/Y_file')
    Y_value = Y*0.10
    
    # Load depth file
    Depth = np.loadtxt('output/dep.out')
    depplot = plt.contourf(X_value, Y_value, Depth, 100)
    plt.title("Water depth (m)")
    plt.colorbar()
    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")
    plt.tight_layout()
    #plt4.savefig("water depth.png")
    #return plt
    plt.show()
    
    
    
    
    
    
    
    
    
    
    
    
    
    