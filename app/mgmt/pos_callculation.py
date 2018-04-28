import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate


class Spline:
    @staticmethod
    def get_spline(x, y):
        tck = interpolate.splrep(x, y, s=0)
        return tck

    @staticmethod
    def evaluate(spline, new_x):
        return interpolate.splev(new_x, spline, der=0)


class PosCalculation:
    x_rel = []  # x position on rope
    x_abs = []  # abs x position on corresponding x_rel position
    z_abs = []  # abs z position on corresponding x_rel position

    x_rel_to_x_abs_spline = Spline.get_spline(x_rel, x_abs)
    x_rel_to_z_abs_spline = Spline.get_spline(x_rel, z_abs)
    x_abs_to_x_rel_spline = Spline.get_spline(x_abs, x_rel)

    @staticmethod
    def calc_x_abs(x_rel):
        """ Returns absolute x position based on distance from line
        :param x_rel:
        :return: absolute x position
        """
        return x_rel  # TODO: insert not an nok cubic spline

    @staticmethod
    def calc_z_abs(x_rel, z_rel):
        z_rope_height = x_rel  # TODO: insert function which gets from x_rel rope height
        return z_rope_height - z_rel

    @staticmethod
    def calc_x_rel(x_abs, x_offset):
        """ Calculates the needed distance to drive from a given absolute x position to another absolute x position with the
        given offset.
        :param x_abs: current absolute x postion
        :param x_offset: needed offset to drive
        :return: relative x to drive to get to new absolute x position
        """
        return x_abs  # TODO: return f^-1(x_abs+x_offset) - f^-1(x_abs), f(x) := calc_x_abs

    @staticmethod
    def calc_abs_x_offset_from_centroid(centroid: int):
        return 310 - centroid

