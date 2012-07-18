import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

from sanitise_input import SanitiseInput

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
        
        