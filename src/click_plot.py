from sanitise_input import SanitiseInput

import numpy as np
import matplotlib.transforms as tfm

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
