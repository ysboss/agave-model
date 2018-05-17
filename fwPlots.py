from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
from matplotlib import animation, rc
from IPython.display import HTML
rc('animation', html='html5')




    
    
def surfacePlot(index):
    # SLURP IN THE DATA
    if (index == 0):
        return
    f = np.genfromtxt("output/output/eta_%05d" % index)
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
    #HTML(anim.to_html5_video())
    return anim

    
def animate2(i):
    global ax
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


def rotatingAnimation(frames):
    size = len(frames)
    fig = plt.figure(figsize=(12,10))
    ax = fig.gca(projection='3d')
    zmin = np.min(frames[0])
    zmax = np.max(frames[0])
    for i in range(1,size):
        zmin = min(zmin,np.min(frames[i]))
        zmax = max(zmax,np.max(frames[i]))
    anim = animation.FuncAnimation(fig, animate2, frames=size, interval=200, repeat=True)
    HTML(anim.to_html5_video())
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    