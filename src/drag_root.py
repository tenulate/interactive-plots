from drag_plot import DragPlot

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