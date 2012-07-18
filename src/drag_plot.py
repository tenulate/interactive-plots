from click_plot import ClickPlot
from errors import DimensionMismatch

class DragPlot(ClickPlot, object):  # object is there so that the super() call in __init__ works
    '''allow the data points of a 'line' to be dragged and changed'''
    
    lock = None # only 1 point dragged at a time
    
    def __init__(self, line, label=None, select_radius=0.1):
        
        super(DragPlot, self).__init__(line, label=label)
        self.index = None               # index to selected data point
        self.background = None          # axis background image - used for smooth animation
        self.selected_point = self.make_selected_point() # a mark to indicate selected data
        self.select_radius = select_radius # tolerance of clicking to select point in axis units
        self.connect()                  # connect events
    
    def connect(self):
        # connect all gui related events 
        self.cidpress = self.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        
    def disconnect(self):
        # disconnect all the stored connection ids
        self.line.figure.canvas.mpl_disconnect(self.cidpress)
        self.line.figure.canvas.mpl_disconnect(self.cidrelease)
        self.line.figure.canvas.mpl_disconnect(self.cidmotion) 
        
    def on_press(self, event):
        # make sure click is in this axis and DragPlot isn't locked
        if event.inaxes != self.axis: return
        if DragPlot.lock is not None: return
        
        # get location of click
        x_click = event.xdata
        y_click = event.ydata
        
        # get closest point information
        index, distance = self.get_closest_point_axis(x_click,y_click)
        if distance > self.select_radius: 
            return
        else:
            # We've picked this point, lock all others
            DragPlot.lock = self
            self.index = index
        
            # draw everything but the selected line & text label and store it in pixel buffer
            # set selected dx > self.select_radius or dytext and point to "animated"
            self.line.set_animated(True)
            if self.text is not None:
                self.text[index].set_animated(True)
            
            # move selected point 
            self.selected_point.set_xdata(self.line.get_xdata()[index])
            self.selected_point.set_ydata(self.line.get_ydata()[index])
            
            # draw everything on canvas except animated objects save as background
            self.canvas.draw()
            self.background = self.canvas.copy_from_bbox(self.axis.bbox)
            
            # now redraw just the line and text and selected point
            self.axis.draw_artist(self.line)
            self.axis.draw_artist(self.selected_point)
            if self.text is not None:
                self.axis.draw_artist(self.text[index])
            
            # and blit just the redrawn area
            self.canvas.blit(self.axis.bbox)

    def on_motion(self, event):
        # on motion we will move the line (and text) if the mouse is over us
        if event.inaxes != self.axis: return
        if self.index is None: return
        if DragPlot.lock is not self: return
        
        # index of selected point
        i = self.index
        
        # move selected point
        self.move_point(event.xdata, event.ydata)
        
        # restore the background region
        self.canvas.restore_region(self.background)

        # redraw just the current line and text label
        self.fig.draw_artist(self.line)
        if self.text is not None:
            self.fig.draw_artist(self.text[i])
        self.fig.draw_artist(self.selected_point)

        # blit just the redrawn area
        self.canvas.blit(self.axis.bbox)
        
    def on_release(self, event):
        # Make sure DragPlot was locked to self
        if event.inaxes != self.axis: return
        if DragPlot.lock is not self: return
        
        # turn off the animation property
        self.line.set_animated(False)    
        
        # restore the background region
        self.canvas.restore_region(self.background)
        
        # draw lines / texts etc...
        self.fig.draw_artist(self.line)
        if self.text is not None and self.index is not None:
            self.text[self.index].set_animated(False)
            self.fig.draw_artist(self.text[self.index])
        
        # blit just the redrawn area
        self.canvas.blit(self.axis.bbox)
        
        # reset data and unlock
        self.index = None
        self.background = None
        DragPlot.lock = None
        
    def move_point(self, new_x, new_y):
        # moves the selected point (indexed by self.index) to new coordinates
        xdata = self.line.get_xdata() # get_xdata().copy() had to be used in past
        ydata = self.line.get_ydata()
        
        # change the i'th x,y point
        i = self.index
        xdata[i] = new_x
        ydata[i] = new_y
        self.set_xdata(xdata)
        self.set_ydata(ydata)
        
        # change the location of the select marker
        self.selected_point.set_xdata(self.line.get_xdata()[i])
        self.selected_point.set_ydata(self.line.get_ydata()[i])
        
    def make_selected_point(self):
        # Highlight for the selected data point
        # Creates an extra point that is larger and transparent then data points
        # animated=True makes it invisible (no points are selected initially)
        size = 3*self.line.get_markersize()
        color = self.line.get_markerfacecolor()
        point, = self.axis.plot(0,0,'o', 
                            markersize=size, alpha=0.4,
                            color=color, animated=True)
        return point


if __name__ == '__main__':
    
    import numpy as np
    import matplotlib.pyplot as plt
    
    # test DragPlot
    xs = np.random.rand(5)*np.pi*400
    ys = np.sin(xs)
    x = np.linspace(0,400*np.pi,100)
    y = np.sin(x)
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    line, = ax.plot(x,y)
    points, = ax.plot(xs,ys, marker='o', linestyle='', markersize=6, color='red')
    label=['a','b','c','d','hi']
    try:
        drag_point = DragPlot(points, label=label)
    except DimensionMismatch, NoPlot:
        drag_point = DragPlot(points)
    
    
    plt.show()
