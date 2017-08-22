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

        self.segments_x = []
        self.segments_y = []
        self.segments_z = []

        self.lines = {}

        self.data = []

    def get_bounds(self):
        """
        Returns the maximum and the minimum value on each axis.
        """
        return {
            'min_x': min(sum(self.segments_x, [])),
            'max_x': max(sum(self.segments_x, [])),
            'min_y': min(sum(self.segments_y, [])),
            'max_y': max(sum(self.segments_y, [])),
            'min_z': min(sum(self.segments_z, [])),
            'max_z': max(sum(self.segments_z, []))
        }

    def compute_data(self, gcode, **kwargs):
        """
        Draws a gcode file.

        :param gcode: The gcode.
        :type gcode: str
        """
        current_pos = [0, 0, 0]

        self.segments_x = []
        self.segments_y = []
        self.segments_z = []

        segment_no = 0

        for t in parse(gcode):
            if t['name'] == '__error__':
                self.parse_error.emit(t['line'])
                break
            
            if t['name'] is not 'G':
                continue

            current_line = t['line']

            x, y, z = current_pos
            x = t['args'].get('X', x)
            y = t['args'].get('Y', y)
            z = t['args'].get('Z', z)

            x_o, y_o, z_o = current_pos

            if t['value'] in (0, 1):
                self.segments_x.append([x_o, x])
                self.segments_y.append([y_o, y])
                self.segments_z.append([z_o, z])
                self.lines[segment_no] = t['line']
                segment_no += 1
            elif t['value'] in (2, 3):
                i = t['args'].get('I', 0)
                j = t['args'].get('J', 0)

                clockwise = (t['value'] == 2)

                nb_segments = 0
                for x_c, y_c in arc_to_segments((x_o, y_o), (i, j), (x, y), clockwise):
                    self.segments_x.append([x_o, x_c])
                    self.segments_y.append([y_o, y_c])
                    x_o, y_o = x_c, y_c
                    nb_segments += 1

                points_z = np.linspace(z_o, z, nb_segments+1)
                for z_count in range(nb_segments):
                    self.segments_z.append([points_z[z_count], points_z[z_count+1]])
                    self.lines[segment_no] = t['line']
                    segment_no += 1

            current_pos = x, y, z

    def draw(self, **kwargs):
        """
        :param reverse_x: Should the x axis be reversed ? (default : False)
        :param reverse_y: Should the y axis be reversed ? (default : False)
        :param reverse_z: Should the z axis be reversed ? (default : False)
        :param highlight_line: A line which is to be highlighted. (default :
            None)
        
        :type highlight_line: int
        :type reverse_x: bool
        :type reverse_y: bool
        :type reverse_z: bool
        """
        self.axes.clear()

        self.axes.set_xlabel(_translate('View3D', 'X Axis'))
        self.axes.set_ylabel(_translate('View3D', 'Y Axis'))
        self.axes.set_zlabel(_translate('View3D', 'Z Axis'))

        reverse_x = kwargs.get('reverse_x', False)
        reverse_y = kwargs.get('reverse_y', False)
        reverse_z = kwargs.get('reverse_z', False)

        def reverse_func(x,y,z):
            if reverse_x :
                x *= -1
            if reverse_y :
                y *= -1
            if reverse_z :
                z *= -1
            return (x,y,z)

        highlight_line = kwargs.get('highlight_line', None)

        min_z = min(sum(self.segments_z, [])) * (1 if not reverse_z else -1)
        max_z = max(sum(self.segments_z, [])) * (1 if not reverse_z else -1)
        map_z_to_ratio = lambda z : (z - min_z) / (max_z - min_z)
        map_z_to_color = lambda z : (1-map_z_to_ratio(z), 0.5, map_z_to_ratio(z))

        segments = []
        for x,y,z in zip(self.segments_x, self.segments_y, self.segments_z):
            segments.append((
                reverse_func(x[0], y[0], z[0]), 
                reverse_func(x[1], y[1], z[1])
            ))
        colors = []
        for l, p in enumerate(segments):
            if self.lines[l] == highlight_line:
                colors.append((0,1,0))
            else:
                colors.append(map_z_to_color((p[0][2]+p[1][2])/2))

        lines = LineCollection(segments, 
            linewidths=1,
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
            [min(sum(self.segments_x, [])), max(sum(self.segments_x, []))],
            [min(sum(self.segments_y, [])), max(sum(self.segments_y, []))],
            [min(sum(self.segments_z, [])), max(sum(self.segments_z, []))],
        ])
        sz = extents[:, 1] - extents[:, 0]
        centers = np.mean(extents, axis=1)
        maxsize = max(abs(sz))
        r = maxsize/2
        for ctr, dim in zip(centers, 'xyz'):
            getattr(self.axes, 'set_{}lim'.format(dim))(ctr - r, ctr + r)

        super(View3D, self).draw()
