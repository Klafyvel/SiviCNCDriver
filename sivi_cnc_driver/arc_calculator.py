from math import atan2, cos, sin, sqrt

from .settings import logger


def arc_to_segments(start, vect_to_center, end, clockwise=False):
    radius = sqrt(vect_to_center[0]**2 + vect_to_center[1]**2)
    start_angle = atan2(-vect_to_center[1], -vect_to_center[0])
    end_angle = atan2(end[1]-start[1]-vect_to_center[1], end[0]-start[0]-vect_to_center[0])

    center = (start[0]+vect_to_center[0], start[1]+vect_to_center[1])
    nb_step = int(abs((end_angle-start_angle)*radius))

    arc_length = end_angle - start_angle
    logger.debug("Arc to segments : start_angle={start_angle}, end_angle={end_angle}, radius={radius}, arc_length={arc_length}".format(**locals()))


    logger.debug(arc_length * radius)

    if arc_length * radius < 2 :
        yield start
        yield end
    else:
        if clockwise:
            d_angle = -1 / radius
        else:
            d_angle = 1 / radius
        angle = start_angle
        for _ in range(nb_step):
            yield center[0] + radius*cos(angle), center[1] + radius*sin(angle)
            angle += d_angle
        yield end