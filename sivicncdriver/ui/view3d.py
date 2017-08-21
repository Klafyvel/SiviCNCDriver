import matplotlib

matplotlib.use('Qt5Agg')
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D


from sivicncdriver import settings
from sivicncdriver.settings import logger
from sivicncdriver.gcode import parse
from sivicncdriver.arc_calculator import arc_to_segments


import matplotlib.pyplot as pl

def axisEqual3D(ax):
    extents = np.array([getattr(ax, 'get_{}lim'.format(dim))() for dim in 'xyz'])
    sz = extents[:,1] - extents[:,0]
    centers = np.mean(extents, axis=1)
    maxsize = max(abs(sz))
    r = maxsize/2
    for ctr, dim in zip(centers, 'xyz'):
        getattr(ax, 'set_{}lim'.format(dim))(ctr - r, ctr + r)

class View3D(FigureCanvas):
    """
    Prints G-Codes in 3D.
    """
    parse_error = pyqtSignal(int)

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111, projection='3d')

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        self.axes.mouse_init()
        

        FigureCanvas.setSizePolicy(self,
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        FigureCanvas.updateGeometry(self)

        self.min_x, self.max_x, self.min_y, self.max_y, self.min_z, self.max_z = 0, 0, 0, 0, 0, 0

    def get_bounds(self):
        """
        Returns the maximum and the minimum value on each axis.
        """
        return {
        'min_x' : self.min_x,
        'max_x' : self.max_x,
        'min_y' : self.min_y,
        'max_y' : self.max_y,
        'min_z' : self.min_z,
        'max_z' : self.max_z
        }

    def draw_file(self, gcode, **kwargs):
        """
        Draws a gcode file.

        :param gcode: The gcode.
        :param highlight_line: A line which is to be highlighted. (default : None)
        :param reverse_x: Should the x axis be reversed ? (default : False)
        :param reverse_y: Should the y axis be reversed ? (default : False)
        :param reverse_z: Should the z axis be reversed ? (default : False)        
        :type highlight_line: int
        :type gcode: str
        :type reverse_x: bool
        :type reverse_y: bool
        :type reverse_z: bool
        """
        current_pos = [0, 0, 0]
        self.min_x, self.max_x = 0, 0
        self.min_y, self.max_y = 0, 0
        self.min_z, self.max_z = 0, 0

        reverse_x = kwargs.get('reverse_x', False)
        reverse_y = kwargs.get('reverse_y', False)
        reverse_z = kwargs.get('reverse_z', False)

        highlight_line = kwargs.get('highlight_line', None)

        self.axes.cla()

        logger.debug("Matplotlib drawing.")

        for t in parse(gcode):
            if t['name'] == '__error__':
                self.parse_error.emit(t['line'])

            current_line = t['line']

            x,y,z = current_pos
            x = t['args'].get('X', x)
            y = t['args'].get('Y', y)
            z = t['args'].get('Z', z)

            x_o, y_o, z_o = current_pos

            if t['value'] in (0,1):
                self.axes.plot([x_o, x], [y_o, y], [z_o, z], color="orange")
            elif t['value'] in (2,3):
                i = t['args'].get('I', 0)
                j = t['args'].get('J', 0)

                clockwise = (t['value'] == 2)

                points = list(zip(*arc_to_segments((x_o,y_o), (i,j), (x,y), clockwise)))
                points_z = np.linspace(z_o, z, len(points[0]))

                self.axes.plot(points[0], points[1], points_z, color="orange")
            current_pos = x, y, z

        axisEqual3D(self.axes)
        self.draw()




class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class SomeCanvas(MyMplCanvas):
    """Simple canvas with a sine plot."""

    def compute_initial_figure(self):
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(2*np.pi*t)
        self.axes.plot(t, s)