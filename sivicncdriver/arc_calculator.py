"""
The arc_calculator module
=========================

It creates small segments from an arc given with G-codes parameters : origin,
end, path to center and sense of rotation.

:Example:

>>> from arc_calculator import arc_to_segments
>>> a = arc_to_segments((0,0),(5,0),(10,0))
>>> for x,y in a:
...     print((x,y))
...
(0.0, 6.12323e-16)
(0.09966, -0.993334)
(0.39469, -1.94708)
(0.87331, -2.8232)
(1.51646, -3.58677)
(2.29848, -4.20735)
(3.1882, -4.66019)
(4.15015, -4.92725)
(5.14598, -4.99787)
(6.136, -4.86924)
(7.08072, -4.54649)
(7.94249, -4.04249)
(8.68696, -3.37733)
(9.28444, -2.57752)
(9.71111, -1.67495)
(10, 0)

"""
from math import atan2, cos, sin, sqrt, pi
from decimal import *

from sivicncdriver.settings import logger


getcontext().prec = 6


def arc_to_segments(start, vect_to_center, end, clockwise=False, length=1,):
    """
    Creates small segments from an arc.

    Uses Decimal for better precision. It yields the vertices.

    :param start: The starting position
    :param vect_to_center: A vector to go to the center of the arc from the
        starting position
    :param end: The ending position
    :param clockwise: Should it go clockwise ?
    :param length: length of the segments 
    :type start: A float tuple
    :type vect_to_center: A float tuple
    :type end: A float tuple
    :type clockwise: bool
    :type length: float
    :return: None, it yields vertices.
    """

    v = Decimal(vect_to_center[0]), Decimal(vect_to_center[1])
    e = Decimal(end[0]), Decimal(end[1])
    s = Decimal(start[0]), Decimal(start[1])
    radius = (v[0]**2 + v[1]**2).sqrt()
    start_angle = Decimal(atan2(-v[1], -v[0])) % Decimal(2*pi)
    center = (s[0]+v[0], s[1]+v[1])
    end_angle = Decimal(atan2(e[1]-center[1], e[0]-center[0])) 

    if clockwise:
        arc_length = -Decimal(2*pi) + (end_angle - start_angle)
    else:
        arc_length = (end_angle - start_angle)

    arc_length = arc_length % Decimal(2*pi)
    if arc_length < 0 and not clockwise:
        arc_length += Decimal(2*pi)
    elif arc_length > 0 and clockwise:
        arc_length -= Decimal(2*pi)
    nb_step = int(abs(arc_length*radius/Decimal(length)))
    
    if abs(arc_length * radius) < length:
        yield start
        yield end
    else:
        d_angle = arc_length / nb_step
        angle = start_angle
        for _ in range(nb_step):
            yield (
                    float(center[0] + radius*Decimal(cos(angle))), 
                    float(center[1] + radius*Decimal(sin(angle)))
                  )
            angle += d_angle
        yield end
