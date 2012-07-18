''' tests functions written in myplot, by setting up GUI stuff. These are not
automated tests '''

from interactive_plot import *

def check_ZoomPlot():
    # test if ZoomPlot adds buttons, and allows specific plots to be zoomed in
    # set data
    
    # make figures, axis, lines
    fig = plt.figure()
    ax1 = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)
    
    # set axis limits
    ax1.set_xlim(-1.0,4*np.pi)

    # make a horizontal rule for zero
    ax1.axhspan(0,0, linewidth=1, linestyle='dashed')
    
    # Test ZoomPlot
    
    f1 = lambda x: 1/(np.sin(x)+2)
    f2 = lambda x: x
    f3 = lambda x: jn(0,x)
    f4 = lambda x: jn(1,x)
    
    zp1 = ZoomPlot(ax1, f1, x_max=2*np.pi)
    zp2 = ZoomPlot(ax2, f2)
    zp3 = ZoomPlot(ax3, f3, x_max=4*np.pi)
#    zp4 = ZoomPlot(ax4, f4)
    
    zp1.add_buttons()    
    plt.show()

def check_DragPlot():
    # test DragPoint for closest click with skewed axis
    xs = np.random.rand(5)*np.pi*400
    ys = np.sin(xs)
    x = np.linspace(0,400*np.pi,100)
    y = np.sin(x)
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    line, = ax.plot(x,y)
    points, = ax.plot(xs,ys, marker='o', linestyle='', markersize=6, color='red')
    label=['a','b','c','d','hi']
    drag_point = DragPlot(points, label=label)

    plt.show()

def check_DragRoot():
    # test DragPoint for closest click with skewed axis
    xs = np.random.rand(5)*np.pi
    ys = 1000*np.sin(xs)
    x = np.linspace(0,2*np.pi,100)
    y = 1000*np.sin(x)
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    line, = ax.plot(x,y)
    points, = ax.plot(xs,ys, marker='o', linestyle='', markersize=6, color='red')
    label=['a','b','c','d','hi']
    f = lambda x: 1000*np.sin(x)
    drag_point = DragRoot(points, f, label=label)

    plt.show()


if __name__ == '__main__':
    pass
    check_ZoomPlot()