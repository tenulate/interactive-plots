''' Test functionality of DragPlot Class '''

from interactive_plot import DragPlot
from errors import *

from nose.tools import assert_equal, assert_not_equal, assert_almost_equal, assert_raises, raises
from nose import with_setup

import numpy as np
import matplotlib.pyplot as plt

line = None
label = {}