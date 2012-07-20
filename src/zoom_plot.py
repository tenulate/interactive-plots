import numpy as np

from sanitise_input import SanitiseInput

class ZoomPlot(SanitiseInput):
    ''' Given a function and an axis, this allows us to zoom in and out along the 
        x/y axes and have the function updated according to the new range '''
    
    def __init__(self, f, axis=None, x_min=0, x_max=1, Npoints=100):
        
        self.axis = self.sanitise_axis_input(axis)  # axis these plots are in
        self.fig = self.axis.figure     # figure axis is in
        self.canvas = self.fig.canvas   # canvas axis is in
        
        self.f = self.sanitise_function_input(f) # Plotted function
        self.Npoints = Npoints  # Number of x values when plotting f
        
        # x/y values to (initially) plot
        self.x = np.linspace(x_min, x_max, Npoints) 
        self.y = f(self.x)
        self.line, = self.axis.plot(self.x, self.y)
        
    def plot(self, color='blue', linewidth=1):
        ''' plot the function being studied '''
        # convenience variables
        self.line.set_color(color)
        self.line.set_linewidth(linewidth)
        self.canvas.draw()
    
    def set_function(self, f):
        ''' change the function being studied '''
        self.f = self.sanitise_function_input(f)
        
    def get_xlim(self):
        return self.x.min(), self.x.max()
    
    def get_ylim(self):
        return self.y.min(), self.y.max()
        
    def set_xlim(self, x_min=0, x_max=1, draw=True):
        ''' re-plots x, f(x) )with the new x-range '''    
        x = np.linspace(x_min, x_max, self.Npoints)
        y = self.f(x)
        # set line data
        self.line.set_xdata(x)
        self.line.set_ydata(y)
        # save line data
        self.x = x
        self.y = y
        
        # update x limits
        self.axis.set_xlim(x_min, x_max)
        # update the y limits too
        self.axis.set_ylim(y.min(), y.max())
        
        if draw:
            self.canvas.draw()
        
    def set_ylim(self, y_min, y_max, draw=True):
        ''' sets new y range '''
        self.axis.set_ylim(y_min, y_max)
        if draw:
            self.canvas.draw()
            
    def set_Npoints(self, Npoints):
        ''' sets how many data points to use in plotting graph '''
        
        # update the Npoints, x, y data
        self.Npoints = Npoints
        self.x = np.linspace(self.x.min(), self.x.max(), Npoints)
        self.y = self.f(self.x)
        
        # update the line
        self.line.set_xdata(self.x)
        self.line.set_ydata(self.y)
        
    def scale_rules(self, min, max, alpha):
        ''' the set of rules of how to zoom in / out along a number line segment (min, max) '''
        
        if alpha <= 0:
            raise BadZoomScale, "Bad zooming in/out factor - need positive numbers"
        
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
        self.set_xlim(new_x_min, new_x_max, draw=draw)
    
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
        selected.set_ylim(new_y_min, new_y_max, draw=draw)
        
if __name__ == '__main__':
    ''' example usage of a zoomPlot class'''
    
    import matplotlib.pyplot as plt
    
    f = lambda x: np.sin(x)
    
    z = ZoomPlot(f)
    z.set_xlim(0,133*np.pi/4)
    z.set_Npoints(1000)
    z.plot()

    
    plt.show()
