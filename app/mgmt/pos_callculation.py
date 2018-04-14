

def calc_x_abs(x_rel):
    """ Returns absolute x position based on distance from line
    :param x_rel:
    :return: absolute x position
    """
    return x_rel  # TODO: insert not an nok cubic spline


def calc_z_abs(x_rel, z_rel):
    z_rope_height = x_rel  # TODO: insert function which gets from x_rel rope height
    return z_rope_height - z_rel


def calc_x_rel(x_abs, x_offset):
    """ Calculates the needed distance to drive from a given absolute x position to another absolute x position with the
    given offset.
    :param x_abs: current absolute x postion
    :param x_offset: needed offset to drive
    :return: relative x to drive to get to new absolute x position
    """
    return x_abs  # TODO: return f^-1(x_abs+x_offset) - f^-1(x_abs), f(x) := calc_x_abs


def calc_abs_x_offset_from_centroid(centroid: int):
    return 300 - centroid