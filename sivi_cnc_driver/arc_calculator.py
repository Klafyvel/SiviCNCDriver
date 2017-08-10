from math import atan2, cos, sin, sqrt
from decimal import *

from .settings import logger


getcontext().prec = 6

def arc_to_segments(start, vect_to_center, end, clockwise=False):
    v = Decimal(vect_to_center[0]), Decimal(vect_to_center[1])
    e = Decimal(end[0]), Decimal(end[1])
    s = Decimal(start[0]), Decimal(start[1])
    radius = (v[0]**2 + v[1]**2).sqrt()
    start_angle = Decimal(atan2(-v[1], -v[0]))
    end_angle = Decimal(atan2(e[1]-s[1]-v[1], e[0]-s[0]-v[0]))

    center = (s[0]+v[0], s[1]+v[1])
    nb_step = int(abs((end_angle-start_angle)*radius))

    arc_length = end_angle - start_angle
    logger.debug(
        "Arc to segments : start_angle={start_angle}, end_angle={end_angle}, radius={radius}, arc_length={arc_length}".format(**locals()))

    if arc_length * radius < 2:
        yield start
        yield end
    else:
        if clockwise:
            d_angle = -1 / radius
        else:
            d_angle = 1 / radius
        angle = start_angle
        for _ in range(nb_step):
            yield center[0] + radius*Decimal(cos(angle)), center[1] + radius*Decimal(sin(angle))
            angle += d_angle
        yield end
