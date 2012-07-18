from errors import NotAFunction, NotAnAxis, NotALine, \
DimensionMismatch, BadLabelInput

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

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
    