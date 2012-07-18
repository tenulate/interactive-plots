from errors import NotAFunction, NotAnAxis, NotALine, DimensionMismatch, \
    DimensionMismatch, BadLabelInput, BadZoomScale, NotNumpyArray, NotAList

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as tfm
from matplotlib.axes import Axes
from matplotlib.widgets import Button
from scipy.special import jn, yn

class SanitiseInput:
    ''' Class with methods to sanitise expected inputs - making sure that they are
        lines, axis, functions, numpy objects etc... when expected '''
    
    def sanitise_function_input(self, f):
        ''' Make sure f is a function / is callable '''
        if not callable(f):
            raise NotAFunction, "f needs to be a callable function eg. f(x)"
        else:
            # f is callable, but it may take other input like strings / classes
            # make sure it works with single number input calls
            try:
                f(0.0)
            # if this doesn't work then it's either a) Infinite at x=0, which is OK
            # as we're just testing to see if it takes in numbers
            except ZeroDivisionError:
                pass
            except:
                raise NotAFunction, "f needs to operate on numbers eg. f(4)"
            
            return f
            
    def sanitise_axis_input(self, axis):
        ''' Make sure that the axis is good '''
        if isinstance(axis, Axes):
            return axis
        else:
            raise NotAnAxis, "require an Axis (matplotlib.axes.Axes) type"
                
    def sanitise_line_input(self, line):
        ''' Make sure the given input to the class is appropriate
            line needs to be of type Line2D '''
        # Make sure line given is of type line
        if not isinstance(line, plt.Line2D):
            raise NotALine, "ClickPlot(line) - line needs to be object of class Line2D - eg. line = matplotlib.pyplot.plot(x,y)"
        else:
            return line
    
    def sanitise_label_input(self, label):
        ''' label needs to be either 
                1. A list same length as the number of data points in line
                2. A string if there is only 1 data point in line 
            Because of the 2 different ways labels can be handled, this function returns
            a [label] list in order to be uniform '''
            
        # Get number of data points, compare to label size
        N_data_pts = self.line.get_xdata().size
        
        # if no label argument is given - ie label = None, then return None
        if label is None:
            return None
        # if labels are a list, make sure it's same length as number of data pts
        if isinstance(label, list):
            if N_data_pts != len(label):
                raise DimensionMismatch, "need data label for every point - label must have same number of elements as data points in line"
            else:
                return label
        # if label is just a string or number, then make sure there is only 1 data point
        elif isinstance(label, (str, float, int)):
            if N_data_pts != 1:
                raise DimensionMismatch, "can only pass single label point if there is a single data point"
            else:
                return [label]
        else:
            raise BadLabelInput, "ClickPlot(line, label) - label must be either a list, float, str or int"
    
class ClickPlot(SanitiseInput):
    '''functions regarding clicking on plots'''
    
    def __init__(self, line, label=None, label_size=20):
        # plot line to use, and associated axis, figure, canvas
        self.line = self.sanitise_line_input(line)  # data points
        self.axis = self.line.get_axes()    # axis the data points are located in
        self.fig = self.line.get_figure()   # figure the data points are located in
        self.canvas = self.fig.canvas       # canvas ...
        # text labels for each data point
        self.label = self.sanitise_label_input(label)
        # make labels for each data point (with appropriate transform)
        self.make_text(label_size)
            
    def make_text(self, label_size):
        ''' creates text labels for plot '''
        # sanitise input
        if self.label is None:
            self.text = None
            return
        
        # create text labels with same coordinates as data
        self.text = []
        x = self.line.get_xdata()
        y = self.line.get_ydata()
        
        # make transform to shift the object over and up some points
        dx, dy = 3/72., 2/72.
        offset = tfm.ScaledTranslation(dx, dy, self.fig.dpi_scale_trans)
        text_transform = self.axis.transData + offset
        
        # set coordinates
        for i in range(0,len(self.label)):
            t = self.axis.text(x[i], y[i], self.label[i],
                             transform=text_transform, size=label_size)
            self.text.append(t)
    
    def get_xdata(self):
        ''' retrieve x data from line '''
        return self.line.get_xdata()
    
    def get_ydata(self):
        ''' retrieve y data from line '''
        return self.line.get_ydata()
    
    def set_xdata(self,x):
        ''' sets the x-data of the points '''
        self.line.set_xdata(x)
        
        # if there is text data, move them too
        if self.text is None: return
        for i in range(0,len(x)):
            self.text[i].set_x(x[i]) 
        
    def set_ydata(self,y):
        ''' sets the y-data of the points '''
        self.line.set_ydata(y)
        
        # if there is text data, move them too
        if self.text is None: return
        for i in range(0,len(y)):
            self.text[i].set_y(y[i])
            
    def draw(self):
        ''' draw this figure '''
        self.canvas.draw()
        
    def get_closest_point(self, x, y):
        ''' given data coordinates x,y - return the closest point from line data '''
        line_xs = self.line.get_xdata()
        line_ys = self.line.get_ydata()
        distance = np.hypot(x-line_xs,y-line_ys)

        # get closest point index and the x/y distances from the click to the closest point
        min_index = distance.argmin()
        x = line_xs[min_index]
        y = line_ys[min_index]
        
        return min_index, x, y
    
    def get_closest_point_axis(self, x, y):
        ''' given data coordinates x,y - return the closest point from line data
            normalising for the scale of the axis '''
        x_min, x_max = self.axis.get_xlim()
        y_min, y_max = self.axis.get_ylim()
        
        x_range = x_max-x_min
        y_range = y_max-y_min
        line_xs = self.line.get_xdata()
        line_ys = self.line.get_ydata()
        
        distance = np.hypot((x-line_xs)/x_range, (y-line_ys)/y_range)
        
        # get closest point index and the normalised distance from the 
        # click to the closest point
        min_index = distance.argmin()
        min_distance = distance[min_index]
        return min_index, min_distance

class DragPlot(ClickPlot, object):  # object is there so that the super() call in __init__ works
    '''allow the data points of 'line' to be dragged and changed'''
    
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

class DragRoot(DragPlot):
    ''' Similar to DragPlot, but when points are dragged they remain fixed to 
        the function being studied '''
    def __init__(self, line, root_function, label=None, select_radius=0.03):
        self.root_function = root_function
        super(DragRoot, self).__init__(line, label=label, select_radius=select_radius)
        
    def move_point(self, new_x, new_y):
        # moves the selected point (indexed by self.index) to new coordinates
        xdata = self.line.get_xdata() # get_xdata().copy() had to be used in past
        ydata = self.line.get_ydata()
        
        # change the i'th x,y point
        f = self.root_function
        i = self.index
        xdata[i] = new_x
        ydata[i] = f(new_x)
        # if y point is out of axis range, limit it to the the top of the axis
        axis_min, axis_max = self.axis.get_ylim()
        y = ydata[i]
        if y > axis_max:
            ydata[i] = axis_max
        if y < axis_min:
            ydata[i] = axis_min
        self.set_xdata(xdata)
        self.set_ydata(ydata)
        
        # change the location of the select marker
        self.selected_point.set_xdata(self.line.get_xdata()[i])
        self.selected_point.set_ydata(self.line.get_ydata()[i])

class ZoomPlot(SanitiseInput):
    ''' Given a function and an axis, this allows us to zoom in and out along the 
        x/y axes and have the function updated according to the new range '''
    
    selected_ZoomPlot = None
    
    def __init__(self, axis, f, x_min=0, x_max=1, Npoints=100, 
                 border_width=3, border_color='red',
                 line_width=1, line_color='blue'):
        
        self.axis = self.sanitise_axis_input(axis)  # axis these plots are in
        # add a property to axis indicating it is a ZoomPlot
        axis.isZoomPlot = True    
        self.fig = axis.figure              # figure axis is in
        self.canvas = axis.figure.canvas    # canvas axis is in
        
        self.f = self.sanitise_function_input(f) # Plotted function
        self.Npoints = Npoints  # Number of x values when plotting f
        self.f_line = None      # plotted line for function
        
        # x/y values to (initially) plot
        self.x = np.linspace(x_min, x_max, Npoints) 
        self.y = f(self.x)

        # highlight and line options
        self.line_width = line_width
        self.line_color = line_color
        self.border_width = border_width      # width of highlighted border
        self.border_color = border_color      # color of highlight
        
        self.connect()  # connect events
        self.plot(color=line_color, line_width=line_width)     # plot the data
    
    def plot(self, color='blue', line_width=1):
        ''' plot the function being studied '''
        # convenience variables
        x, y = self.x, self.y

        # plot the line
        self.f_line, = self.axis.plot(x, y, color=color, linewidth=line_width)
        self.axis.set_xlim(self.get_xrange(x))
        self.axis.set_ylim(self.get_yrange(y))
        self.canvas.draw()
    
    def set_function(self, f):
        ''' change the function being studied '''
        self.f = self.sanitise_function_input(f)
        
    def get_xrange(self,x):
        return x.min(), x.max()
    
    def get_yrange(self,y):
        return y.min(), y.max()
        
    def set_xrange(self, x_min=0, x_max=1, draw=True):
        ''' re-plots x, f(x) with the new x-range '''    
        x = np.linspace(x_min, x_max, self.Npoints)
        y = self.f(x)
        # set line data
        self.f_line.set_xdata(x)
        self.f_line.set_ydata(y)
        # update x limits
        self.axis.set_xlim(x_min, x_max)
        if draw:
            self.canvas.draw()
        
        # save line data
        self.x = x
        self.y = y
        
    def set_yrange(self, y_min, y_max, draw=True):
        ''' sets new y range, does not re-plot data '''
        self.axis.set_ylim(y_min, y_max)
        if draw:
            self.canvas.draw()
        
    def scale_rules(self, min, max, alpha):
        ''' the set of rules of how to zoom in / out along a number line segment (min, max) '''
        get_off_zero = 0.1
        
        if alpha <= 0:
            raise BadZoomScale, "Bad zooming in/out factor - need positive numbers"
        
        else:
            # keep axis centered where it is
            length = max-min
            mid_point = (max+min)/2
            
            new_max = mid_point+0.5*length*alpha
            new_min = mid_point-0.5*length*alpha
            
        return new_min, new_max
            
    def scale_x(self, alpha=1.2, draw=True):
        ''' zooms in/out along x axis ''' 
        # get current x limits
        x_min, x_max = self.axis.get_xlim()
        new_x_min, new_x_max = self.scale_rules(x_min, x_max, alpha)
        # set new range
        self.set_xrange(new_x_min, new_x_max, draw=draw)
    
    def scale_y(self, alpha=1.2, draw=True):
        # get the currently selected ZoomPlot
        if ZoomPlot.selected_ZoomPlot is None:
            return
        else:
            selected = ZoomPlot.selected_ZoomPlot
            ax = selected.axis
        
        # get current y limits
        y_min, y_max = ax.get_ylim()
        new_y_min, new_y_max = self.scale_rules(y_min, y_max, alpha)
        # set new range
        selected.set_yrange(new_y_min, new_y_max, draw=draw)
    
    def connect(self):
        # connect necessary events
        self.cid_press = self.canvas.mpl_connect('button_press_event', self.on_press_axis)
        self.cid_scroll = self.canvas.mpl_connect('scroll_event', self.on_scroll)
        
        # change x/y scales
        # only the first ZoomPlot will have these button axes as a property
        # we wish to connect these events only once
        try:
            self.xmore_axis
            self.xless_axis
            self.ymore_axis
            self.yless_axis
        except:
            return
        
        # all these button axes exist, connect them
        self.cid_xmore = self.canvas.mpl_connect('button_press_event', self.on_press_xmore)
        self.cid_xless = self.canvas.mpl_connect('button_press_event', self.on_press_xless)
        self.cid_ymore = self.canvas.mpl_connect('button_press_event', self.on_press_ymore)
        self.cid_yless = self.canvas.mpl_connect('button_press_event', self.on_press_yless)
    
    def disconnect(self):
        # disconnect event signals
        self.canvas.mpl_disconnect(self.cid_press)
        try:
            self.canvas.mpl_disconnect(self.cid_xmore)
            self.canvas.mpl_disconnect(self.cid_xless)
            self.canvas.mpl_disconnect(self.cid_ymore)
            self.canvas.mpl_disconnect(self.cid_yless)  
        except:
            return 
        
    def on_press_axis(self, event):
        # if we havn't clicked on an axis don't do anything
        if event.inaxes is None:
            return
        
        # check that the axis has the property "isZoomPlot" and that it's true
        try:    
            event.inaxes.isZoomPlot == True
            pass
        except: 
            return
        
        # if we've already selected this axis don't bother doing anything
        if ZoomPlot.selected_ZoomPlot is not None \
        and ZoomPlot.selected_ZoomPlot.axis == event.inaxes:
            return
        
        # we've clicked on a ZoomPlot axis by now
        if ZoomPlot.selected_ZoomPlot is None:
            ZoomPlot.selected_ZoomPlot = self
        
        # if a previous axis was highlighted, get rid of its highlight
        if ZoomPlot.selected_ZoomPlot.axis is not None:
            ZoomPlot.selected_ZoomPlot.axis.patch.set_linewidth(0)
        
        # make clicked axis the selected one
        ZoomPlot.selected_ZoomPlot = self
        
        # make a new highlighted square over this axis
        highlight = event.inaxes.patch
        highlight.set_linewidth(self.border_width)
        highlight.set_edgecolor(self.border_color)
        self.canvas.draw()
    
    def on_scroll(self, event):
        'when scrolling mouse wheel zoom in / out on current axis'
        scroll_rate = 1.05
        
        # if we havn't clicked on an axis don't do anything
        if (event.inaxes is None) or (event.inaxes is not self.axis):
            return
        
        # check that the axis has the property "isZoomPlot" and that it's true
        try:    
            event.inaxes.isZoomPlot == True
            pass
        except: 
            return
        
        if not (ZoomPlot.selected_ZoomPlot is self):
            return
        
        if event.button is 'up':
            self.scale_x(scroll_rate, draw=False)
            self.scale_y(scroll_rate, draw=False)
        elif event.button is 'down':
            self.scale_x(1./scroll_rate, draw=False)
            self.scale_y(1./scroll_rate, draw=False)
        
        self.f_line.draw()
        
    def on_press_xmore(self, event):
        # check that the click occured on the xmore button
        if event.inaxes != self.xmore_axis: return
        
        # make sure an axes is selected
        if ZoomPlot.selected_ZoomPlot is None: return
        
        selected = ZoomPlot.selected_ZoomPlot
        
        # scale the x values 
        selected.scale_x(alpha=1.5)

    def on_press_xless(self, event):
        # check that the click occured on the xless button
        if event.inaxes != self.xless_axis: return
        
        # make sure an axes is selected
        if ZoomPlot.selected_ZoomPlot is None: return
        
        selected = ZoomPlot.selected_ZoomPlot
        
        # scale the x values 
        selected.scale_x(alpha=1.0/1.5)
        
    def on_press_ymore(self, event):
        # check that the click occured on the ymore button
        if event.inaxes != self.ymore_axis: return
        
        # make sure an axes is selected
        if ZoomPlot.selected_ZoomPlot is None: return
        
        # scale the y values 
        self.scale_y(alpha=1.5)
        
    def on_press_yless(self, event):
        # check that the click occured on the yless button
        if event.inaxes != self.yless_axis: return
        
        # make sure an axes is selected
        if ZoomPlot.selected_ZoomPlot is None: return
        
        # scale the y values 
        self.scale_y(alpha=1.0/1.5)            
    
    def add_buttons(self, color='0.85', hover='0.95'):
        # if buttons have already been added to this figure, don't add them again
        try:
            if self.fig.ZoomPlotButtons:
                return
        except:
            pass
        
        # adds buttons to the bottom of the figure
        self.fig.subplots_adjust(bottom=0.15)
        
        # make button axes
        self.xmore_axis = plt.axes([0.01, 0.025, 0.12, 0.07])
        self.xless_axis = plt.axes([0.14, 0.025, 0.12, 0.07])
        self.ymore_axis = plt.axes([0.27, 0.025, 0.12, 0.07])
        self.yless_axis = plt.axes([0.40, 0.025, 0.12, 0.07])

        # place buttons in axes
        xmore_button = Button(self.xmore_axis, 'zoom out X', color=color, hovercolor=hover)
        xless_button = Button(self.xless_axis, 'zoom in X', color=color, hovercolor=hover)
        ymore_button = Button(self.ymore_axis, 'zoom out Y', color=color, hovercolor=hover)
        yless_button = Button(self.yless_axis, 'zoom in Y', color=color, hovercolor=hover)
        
        # add an indication to the figure that buttons have been added
        self.fig.ZoomPlotButtons = True
        
        # connect buttons
        self.connect()


if __name__ == '__main__':
    
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