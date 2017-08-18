"""
A bunch of command to easily create G-Codes.
"""

def step(axis, n):
    """
    Moves the given axis of n steps.

    :param axis: The axis
    :param n: number of steps
    :type axis: str
    :type n: int
    """
    return "S0 {}{}".format(axis,n)

def step_x(n):
    """
    Moves the X axis oh n steps.
    :param n: The number of steps
    :type n: int
    """
    return step('X', n)

def step_y(n):
    """
    Moves the Y axis oh n steps.
    :param n: The number of steps
    :type n: int
    """
    return step('Y', n)

def step_z(n):
    """
    Moves the Z axis oh n steps.
    :param n: The number of steps
    :type n: int
    """
    return step('Z', n)

def start_continuous(axis, direction="forward"):
    """
    Start a continuous movement in the given direction.
    :param axis: The axis which is to move.
    :param direction: The direction.
    :type axis: str
    :type direction: str
    """
    if direction == "forward":
        return "S1 {}".format(axis)
    else:
        return "S2 {}".format(axis)

def start_continuous_x_forward():
    """
    Start a continuous movement on X axis forward.
    """
    return start_continuous("X")

def start_continuous_y_forward():
    """
    Start a continuous movement on Y axis forward.
    """
    return start_continuous("Y")

def start_continuous_z_forward():
    """
    Start a continuous movement on Z axis forward.
    """
    return start_continuous("Z")

def start_continuous_x_backward():
    """
    Start a continuous movement on X axis backward
    """
    return start_continuous("X", "backward")

def start_continuous_y_backward():
    """
    Start a continuous movement on Y axis backward
    """
    return start_continuous("Y", "backward")

def start_continuous_z_backward():
    """
    Start a continuous movement on Z axis backward
    """
    return start_continuous("Z", "backward")

def stop(axis):
    """
    Stop any movement on the given axis.
    """
    return "S3 {}".format(axis)

def stop_x():
    """
    Stop any movement on the X axis.
    """
    return stop("X")

def stop_y():
    """
    Stop any movement on the Y axis.
    """
    return stop("Y")

def stop_z():
    """
    Stop any movement on the Z axis.
    """
    return stop("Z")

def emergency_stop():
    """
    Stop every axis.
    """
    return "M112"

def set_origin():
    """
    Register the current position as the origin.
    """
    return "G92 X000 Y000 Z000"

def goto_origin():
    """
    Go to the origin.
    """
    return "G28"

def config_as_gcode(**kwargs):
    """
    Make a set of commands to save the configuration.

    :param x_ratio: The X axis ratio (mm/step)
    :param y_ratio: The Y axis ratio (mm/step)
    :param z_ratio: The Z axis ratio (mm/step)

    :param x_drive: X axis drive mode (0:normal, 1:full torque, 2:half step)
    :param y_drive: Y axis drive mode (0:normal, 1:full torque, 2:half step)
    :param z_drive: Z axis drive mode (0:normal, 1:full torque, 2:half step)

    :param x_play: X axis play
    :param y_play: Y axis play
    :param z_play: Z axis play

    :param x_reverse: Should the X axis be reversed ?
    :param y_reverse: Should the Y axis be reversed ?
    :param z_reverse: Should the Z axis be reversed ?

    :param x_min_time: The minimal duration between 2 pulse for the x axis in
        milliseconds.
    :param y_min_time: The minimal duration between 2 pulse for the y axis in
        milliseconds.
    :param z_min_time: The minimal duration between 2 pulse for the z axis in
        milliseconds.

    :type x_ratio: float
    :type y_ratio: float
    :type z_ratio: float

    :type x_drive: int
    :type y_drive: int
    :type z_drive: int

    :type x_play: float
    :type y_play: float
    :type z_play: float

    :type x_reverse: bool
    :type y_reverse: bool
    :type z_reverse: bool

    :type x_min_time: int
    :type y_min_time: int
    :type z_min_time: int
    """

    r = []
    r.append("S4 X{x_ratio} Y{y_ratio} Z{z_ratio}".format(**kwargs))

    drive = [5, 6, 7]
    r.append("S{} X".format(drive[kwargs["x_drive"]]))
    r.append("S{} Y".format(drive[kwargs["y_drive"]]))
    r.append("S{} Z".format(drive[kwargs["z_drive"]]))

    r.append("S8 X{x_play} Y{y_play} Z{z_play}".format(**kwargs))

    reverse = {True:9, False:10}
    r.append("S{} X".format(reverse[kwargs["x_reverse"]]))
    r.append("S{} Y".format(reverse[kwargs["y_reverse"]]))
    r.append("S{} Z".format(reverse[kwargs["z_reverse"]]))

    r.append("S11 X{x_min_time} Y{y_min_time} Z{z_min_time}".format(**kwargs))

    return '\n'.join(r)
