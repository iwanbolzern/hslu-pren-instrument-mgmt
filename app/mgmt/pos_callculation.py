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
    x_rel = [0, 3080, 6144, 9200, 12264, 15336, 18392, 21448, 24496]  # x position on rope
    x_abs = [21.3, 57.2, 93.3, 127.9, 164.1, 199.5, 234.1, 268.7, 302.9]  # abs x position on corresponding x_rel position
    z_abs = [46, 47.3, 49.3, 52.6, 56.7, 61.2, 69.5, 77.3, 86.2]  # abs z position on corresponding x_rel position

    x_rel_to_x_abs_spline = Spline.get_spline(x_rel, x_abs)
    x_rel_to_z_abs_spline = Spline.get_spline(x_rel, z_abs)
    x_abs_to_x_rel_spline = Spline.get_spline(x_abs, x_rel)

    @staticmethod
    def calc_x_abs(x_rel):
        """ Returns absolute x position based on distance from line
        :param x_rel:
        :return: absolute x position
        """
        return Spline.evaluate(PosCalculation.x_rel_to_x_abs_spline, x_rel)

    @staticmethod
    def calc_z_abs(x_rel, z_rel):
        z_rope_height = Spline.evaluate(PosCalculation.x_rel_to_z_abs_spline, x_rel)  # function which gets from x_rel rope height
        return z_rope_height - z_rel

    @staticmethod
    def calc_x_rel(x_abs, x_offset):
        """ Calculates the needed distance to drive from a given absolute x position to another absolute x position with the
        given offset.
        :param x_abs: current absolute x postion
        :param x_offset: needed offset to drive
        :return: relative x to drive to get to new absolute x position
        """
        x_rel_after_offset = Spline.evaluate(PosCalculation.x_abs_to_x_rel_spline, x_abs + x_offset)
        x_rel_on_x_abs = Spline.evaluate(PosCalculation.x_abs_to_x_rel_spline, x_abs)
        return x_rel_after_offset - x_rel_on_x_abs  # return f^-1(x_abs+x_offset) - f^-1(x_abs), f(x) := calc_x_abs

    @staticmethod
    def calc_abs_x_offset_from_centroid(centroid: int):
        return 310 - centroid

