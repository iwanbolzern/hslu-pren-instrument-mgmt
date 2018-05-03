from com.ic_interface import ICInterface, Direction
from mgmt.pos_callculation import Spline, PosCalculation

pos_calc = PosCalculation()
pos_calc.x_rel_to_z_abs_spline

x_rel_new = [i for i in range(25000)]
x_abs_new = [Spline.evaluate(pos_calc.x_rel_to_x_abs_spline, x_rel) for x_rel in x_rel_new]
z_abs_new = [Spline.evaluate(pos_calc.x_rel_to_z_abs_spline, x_rel) for x_rel in x_rel_new]

import matplotlib.pyplot as plt
plt.plot(x_rel_new, z_abs_new, 'o')
plt.legend(['z_abs'], loc='best')
axes = plt.gca()
axes.set_ylim([0, 110])
plt.show()




# x_position_rel = 0
#
#
# def __position_update(x_offset, z_offset):
#     global x_position_rel
#     x_position_rel += x_offset
#     print('x_position_rel: ' + str(x_position_rel))
#
#
# ic_interface = ICInterface()
# ic_interface.register_position_callback(__position_update)
#
# while True:
#     input()
#     ic_interface.drive_distance_async(3000, 60, Direction.Backward, lambda: print('done'))



