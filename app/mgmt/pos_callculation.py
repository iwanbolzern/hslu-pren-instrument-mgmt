from scipy import interpolate


class Spline:
    @staticmethod
    def get_spline(x, y, k=4):
        tck = interpolate.splrep(x, y, s=0, k=k)
        return tck

    @staticmethod
    def evaluate(spline, new_x):
        return interpolate.splev(new_x, spline, der=0).ravel()[0]


class PosCalculation:
    x_rel = [0, 3080, 6144, 9200, 12264, 15336, 18392, 21448, 24496]  # x position on rope
    x_abs = [213, 572, 933, 1279, 1641, 1995, 2341, 2687, 3029]  # abs x position on corresponding x_rel position
    z_abs = [460, 473, 493, 526, 567, 612, 695, 773, 862]  # abs z position on corresponding x_rel position
    z_offset_cube = 300   # Distance from where we measured z to where the cube actually is
    x_middle_for_centroid = [232, 225, 224, 216, 219, 218, 213, 211, 216]
    pixel_to_mm_factor = [0.92, 0.91, 0.96, 1.05, 1.2, 1.3, 1.4, 1.65, 1.85]  # used with x_abs

    x_rel_to_x_abs_spline = Spline.get_spline(x_rel, x_abs)
    x_rel_to_z_abs_spline = Spline.get_spline(x_rel, z_abs)
    x_abs_to_x_rel_spline = Spline.get_spline(x_abs, x_rel)
    x_middle_from_centroid_spline = Spline.get_spline(x_abs, x_middle_for_centroid)
    pixel_to_mm_factor_spline = Spline.get_spline(x_abs, pixel_to_mm_factor)

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
        return z_rope_height - z_rel - PosCalculation.z_offset_cube

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
        return max([x_rel_on_x_abs, x_rel_after_offset]) - min([x_rel_on_x_abs, x_rel_after_offset])  # return f^-1(x_abs+x_offset) - f^-1(x_abs), f(x) := calc_x_abs

    @staticmethod
    def calc_abs_x_offset_from_centroid(abs_x_position: int, centroid: int):
        centroid_position = Spline.evaluate(PosCalculation.x_middle_from_centroid_spline, abs_x_position)
        pixel_to_mm_factor = Spline.evaluate(PosCalculation.pixel_to_mm_factor_spline, abs_x_position)
        return (centroid_position - centroid) * pixel_to_mm_factor
