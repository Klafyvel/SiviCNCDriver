import matplotlib

matplotlib.use('Qt5Agg')
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection as LineCollection


from sivicncdriver import settings
from sivicncdriver.settings import logger
from sivicncdriver.gcode import parse
from sivicncdriver.arc_calculator import arc_to_segments


import matplotlib.pyplot as pl

_translate = QCoreApplication.translate


def axisEqual3D(ax):
    extents = np.array([getattr(ax, 'get_{}lim'.format(dim))()
                        for dim in 'xyz'])
    sz = extents[:, 1] - extents[:, 0]
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

        # self.mpl_connect('key_press_event', self.parent().on_key_press)

        self.points_x = []
        self.points_y = []
        self.points_z = []

        self.data = []

    def get_bounds(self):
        """
        Returns the maximum and the minimum value on each axis.
        """
        return {
            'min_x': min(self.points_x),
            'max_x': max(self.points_x),
            'min_y': min(self.points_y),
            'max_y': max(self.points_y),
            'min_z': min(self.points_z),
            'max_z': max(self.points_z)
        }

    def compute_data(self, gcode, **kwargs):
        """
        Draws a gcode file.

        :param gcode: The gcode.
        :param highlight_line: A line which is to be highlighted. (default : None)    
        :type highlight_line: int
        :type gcode: str
        """
        current_pos = [0, 0, 0]
        self.min_x, self.max_x = 0, 0
        self.min_y, self.max_y = 0, 0
        self.min_z, self.max_z = 0, 0

        highlight_line = kwargs.get('highlight_line', None)

        self.axes.clear()

        self.points_x = []
        self.points_y = []
        self.points_z = []

        logger.debug("Matplotlib drawing.")

        self.axes.set_xlabel(_translate('View3D', 'X Axis'))
        self.axes.set_ylabel(_translate('View3D', 'Y Axis'))
        self.axes.set_zlabel(_translate('View3D', 'Z Axis'))

        self.axes.set_navigate(True)
        logger.debug(self.axes.can_zoom())

        for t in parse(gcode):
            if t['name'] == '__error__':
                self.parse_error.emit(t['line'])

            current_line = t['line']

            x, y, z = current_pos
            x = t['args'].get('X', x)
            y = t['args'].get('Y', y)
            z = t['args'].get('Z', z)

            x_o, y_o, z_o = current_pos

            if t['value'] in (0, 1):
                self.points_x.append(x)
                self.points_y.append(y)
                self.points_z.append(z)
            elif t['value'] in (2, 3):
                i = t['args'].get('I', 0)
                j = t['args'].get('J', 0)

                clockwise = (t['value'] == 2)

                points_x, points_y = list(
                    zip(*arc_to_segments((x_o, y_o), (i, j), (x, y), clockwise)))
                points_z = np.linspace(z_o, z, len(points_x))

                self.points_x.extend(points_x)
                self.points_y.extend(points_y)
                self.points_z.extend(points_z)

            current_pos = x, y, z

    def draw(self, **kwargs):
        """
        :param reverse_x: Should the x axis be reversed ? (default : False)
        :param reverse_y: Should the y axis be reversed ? (default : False)
        :param reverse_z: Should the z axis be reversed ? (default : False)    

        :type reverse_x: bool
        :type reverse_y: bool
        :type reverse_z: bool
        """
        reverse_x = kwargs.get('reverse_x', False)
        reverse_y = kwargs.get('reverse_y', False)
        reverse_z = kwargs.get('reverse_z', False)
        # self.axes.plot(self.points_x, self.points_y, self.points_z)


        min_z = min(self.points_z)
        max_z = max(self.points_z)
        map_z_to_ratio = lambda z : (z - min_z) / (max_z - min_z)
        map_z_to_color = lambda z : (1-map_z_to_ratio(z), 0.5, map_z_to_ratio(z))

        segments = []
        for i in range(len(self.points_z)-1):
            segments.append([
                (self.points_x[i], self.points_y[i], self.points_z[i]),
                (self.points_x[i+1], self.points_y[i+1], self.points_z[i+1]),
            ])
        colors = [map_z_to_color((p[0][2]+p[1][2])/2) for p in segments]
        lines = LineCollection(segments, 
            linewidths=(0.5, 1, 1.5, 2),
            linestyles='solid',
            colors=colors
        )
        self.axes.add_collection3d(lines)
        
        if reverse_x:
            self.axes.invert_xaxis()
        if reverse_y:
            self.axes.invert_yaxis()
        if reverse_z:
            self.axes.invert_zaxis()

        extents = np.array([
            [min(self.points_x), max(self.points_x)],
            [min(self.points_y), max(self.points_y)],
            [min(self.points_z), max(self.points_z)],
        ])
        sz = extents[:, 1] - extents[:, 0]
        centers = np.mean(extents, axis=1)
        maxsize = max(abs(sz))
        r = maxsize/2
        for ctr, dim in zip(centers, 'xyz'):
            getattr(self.axes, 'set_{}lim'.format(dim))(ctr - r, ctr + r)

        super(View3D, self).draw()
