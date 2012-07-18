''' A file to gather all the desired plotting classes - each class is in a 
    separate file, for aesthetic reasons, this file is created so that those 
    multiple file names don't need to be remembered when importing the classes
    
    eg. instead of having
    from click_plot import ClickPlot
    from drag_root import DragRoot
    
    with this interactive_plot.py file, we can now use the following in our code
    from interactive_plot import ClickPlot, DragRoot '''

from click_plot import ClickPlot
from drag_plot import DragPlot
from drag_root import DragRoot
from zoom_plot import ZoomPlot