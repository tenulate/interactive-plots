''' Test functionality of DragPlot Class '''

from interactive_plot import *
from errors import *

from nose.tools import assert_equal, assert_not_equal, assert_almost_equal, assert_raises, raises
from nose import with_setup

import numpy as np
import matplotlib.pyplot as plt

from scipy.special import jn, yn

ax = None
fig = None
zoom = None
f, g, h = None, None, None

def setup_variables():
    'variables used in each test'
    global ax, fig, zoom, f, g, h
    fig = plt.figure()
    ax = [fig.add_subplot(1,2,1), fig.add_subplot(1,2,2)]
    zoom = []
    f = lambda x: 1./(x**2+1)
    g = lambda z: 1/z-10
    zoom.append(ZoomPlot(ax[0], f))
    zoom.append(ZoomPlot(ax[1], g))


@with_setup(setup_variables)    
def test_good_input():
    'ZoomPlot(ax, f) should work with god input'
    ZoomPlot(ax[0], g)
    
@with_setup(setup_variables)    
def test_bad_function_input():
    'zoom = ZoomPlot(ax, f) should fail when f is not a function'
    assert_raises(NotAFunction, ZoomPlot, ax[0], 3)
    assert_raises(NotAFunction, ZoomPlot, ax[0], ClickPlot)
    
@with_setup(setup_variables)    
def test_bad_axis_input():
    'zoom = ZoomPlot(ax, f) should fail when ax is not an axis'
    assert_raises(NotAnAxis, ZoomPlot, 1, f)
    assert_raises(NotAnAxis, ZoomPlot, fig, f)

@with_setup(setup_variables)  
def test_changing_function():
    'ZoomPlot.set_function(new_f) should change the plotted function'
    h = lambda x: np.sin(x/(2*np.pi))
    z = zoom[0]
    z.set_function(h)
    x = np.linspace(0,10)
    assert all(h(x) == z.f(x))
    
@with_setup(setup_variables)
def test_bad_changing_function():
    'ZoomPlot.set_function(f) should fail if f is not a proper function'
    z = zoom[0]
    assert_raises(NotAFunction, z.set_function, 3)
    assert_raises(NotAFunction, z.set_function, ClickPlot)
    
    
if __name__ == '__main__':
    x = np.linspace(0,10)
    y = lambda x: jn(0,x)
    line, = plt.plot([0], [0])
    ax = line.get_axes()
    z = ZoomPlot(ax, y)
    z.add_buttons()
    z.connect()
    plt.show()