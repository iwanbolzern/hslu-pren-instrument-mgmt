from scipy import interpolate


class Spline:
    @staticmethod
    def get_spline(x, y):
        tck = interpolate.splrep(x, y, s=0)
        return tck

    @staticmethod
    def evaluate(spline, new_x):
        return interpolate.splev(new_x, spline, der=0).ravel()[0]


class PosCalculation:
    x_rel = [0, 3080, 6144, 9200, 12264, 15336, 18392, 21448, 24496]  # x position on rope
    x_abs = [213, 572, 933, 1279, 1641, 1995, 2341, 2687, 3029]  # abs x position on corresponding x_rel position
    z_abs = [460, 473, 493, 526, 567, 612, 695, 773, 862]  # abs z position on corresponding x_rel position

    x_rel_to_x_abs_spline = Spline.get_spline(x_rel, x_abs)
    x_rel_to_z_abs_spline = Spline.get_spline(x_rel, z_abs)
    x_abs_to_x_rel_spline = Spline.get_spline(x_abs, x_rel)

    @staticmethod
    def calc_x_abs(x_rel):
        """ Returns absolute x position based on distance from line
        :param x_rel:
        :return: absolute x position
        """
        return int(round(Spline.evaluate(PosCalculation.x_rel_to_x_abs_spline, x_rel)))

    @staticmethod
    def calc_z_abs(x_rel, z_rel):
        z_rope_height = int(round(Spline.evaluate(PosCalculation.x_rel_to_z_abs_spline, x_rel)))  # function which gets from x_rel rope height
        return z_rope_height - z_rel

    @staticmethod
    def calc_x_rel(x_abs, x_offset):
        """ Calculates the needed distance to drive from a given absolute x position to another absolute x position with the
        given offset.
        :param x_abs: current absolute x postion
        :param x_offset: needed offset to drive
        :return: relative x to drive to get to new absolute x position
        """
        x_rel_after_offset = int(round(Spline.evaluate(PosCalculation.x_abs_to_x_rel_spline, x_abs + x_offset)))
        x_rel_on_x_abs = int(round(Spline.evaluate(PosCalculation.x_abs_to_x_rel_spline, x_abs)))
        return x_rel_after_offset - x_rel_on_x_abs  # return f^-1(x_abs+x_offset) - f^-1(x_abs), f(x) := calc_x_abs

    @staticmethod
    def calc_abs_x_offset_from_centroid(centroid: int):
        return 140 - centroid

