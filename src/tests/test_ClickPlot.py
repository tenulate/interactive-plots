''' Test functionality of ClickPlot Class '''

from interactive_plot import ClickPlot
from errors import *

from nose.tools import assert_equal, assert_not_equal, assert_almost_equal, assert_raises, raises
from nose import with_setup

import numpy as np
import matplotlib.pyplot as plt

line = None
label = {}

def setup_variables():
    ''' set up function to create a line '''
    global line
    xs = np.array([4, 3, 22])
    ys = np.array([1, 2, 3])
    line, = plt.plot(xs, ys)
    
    ''' make a dictionary of various labels '''
    global label
    label['short'] = ['a', 'b']
    label['long'] = ['a', 'b', 'c', 'd', 'e']
    label['good'] = ['a', 'b', 'c']
    label['numbers'] = [1, 2, 3]

@with_setup(setup_variables)
def test_good_line_input():
    ''' x = ClickPlot(Z) should pass when Z is a line type '''
    the_plot = ClickPlot(line)

@with_setup(setup_variables)    
def test_bad_line_input():
    ''' x = ClickPlot(Z) - Make sure an Exception is thrown up when Z is not a line class '''
    assert_raises(NotALine, ClickPlot, 3)
    assert_raises(NotALine, ClickPlot, "hi")
    assert_raises(NotALine, ClickPlot, [3])
    assert_raises(NotALine, ClickPlot, ['hi', 3])
    assert_raises(NotALine, ClickPlot, {'name': 3})
    assert_raises(NotALine, ClickPlot, [line])
    
@with_setup(setup_variables)
def test_good_label_input():
    ''' x = ClickPlot(line, label=Z) should be fine if Z is a label list of the right length'''
    the_plot = ClickPlot(line, label=label['good'])
    the_plot = ClickPlot(line, label=label['numbers'])

@with_setup(setup_variables)
def test_bad_label_input():
    ''' x = ClickPlot(line, label=Z) should fail if Z is not a list, or doesn't have a label for each data point '''
    assert_raises(DimensionMismatch, ClickPlot, line, label=label['short'])
    assert_raises(DimensionMismatch, ClickPlot, line, label=label['long'])
    assert_raises(DimensionMismatch, ClickPlot, line, label=3)
    assert_raises(DimensionMismatch, ClickPlot, line, label='abc')
    assert_raises(BadLabelInput, ClickPlot, line, label={'hi': 3})

@with_setup(setup_variables)
def test_single_label_input():
    ''' ClickPlot(line, label='single label') should work if line only has a single data point '''
    x, y = 0, 0
    line, = plt.plot(x, y)
    names = ['origin', 1, 1.77]
    for name in names:
        plot = ClickPlot(line, label=name)
        assert_equal(plot.label, [name])

def test_closest_point():
    ''' ClickPlot.get_closest_point(x,y) should return an index to and the coordinates of the data point closest to (x,y) '''
    points = [(0,0), (10,0), (10,10), (0,10)]
    clicks = [(0,0), (6,6), (5,5)]
    answers = [(0,0,0), (2,10,10), (0,0,0)]
    
    xdata, ydata = [], []
    for point in points:
        xdata.append(point[0])
        ydata.append(point[1])
    
    line, = plt.plot(xdata, ydata)
    plot = ClickPlot(line)

    for i in range(len(clicks)):
        click_x, click_y = clicks[i][0], clicks[i][1]
        ans_index, ans_x, ans_y = answers[i][0], answers[i][1], answers[i][2]
        index, x, y = plot.get_closest_point(click_x, click_y)
        print "answer: index, x, y = ", ans_index, ans_x, ans_y
        print "function: index, x, y = ", index, x, y
        assert_equal( (index, x, y), (ans_index, ans_x, ans_y))

def test_closest_point_axis():
    ''' test closest point relative to axis coordinates '''
    
    x = [950, 1000]
    y = [10, 1]
    click_x, click_y = 950, 1
    
    line, = plt.plot(x,y)
    plot = ClickPlot(line)
    plot.axis.set_xlim(0, 1000)
    plot.axis.set_ylim(0, 1)
    
    index, dist = plot.get_closest_point_axis(click_x, click_y)
    assert index == 1   
    