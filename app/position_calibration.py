from com.ic_interface import ICInterface, Direction

x_position_rel = 0


def __position_update(x_offset, z_offset):
    global x_position_rel
    x_position_rel += x_offset
    print('x_position_rel: ' + str(x_position_rel))


ic_interface = ICInterface()
ic_interface.register_position_callback(__position_update)

while True:
    input()
    ic_interface.drive_distance_async(3000, 60, Direction.Backward, lambda: print('done'))



