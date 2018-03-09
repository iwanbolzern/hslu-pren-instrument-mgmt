from collections import defaultdict
from enum import Enum
from threading import Event
from typing import List, Callable

from app.com.ic_communication import ICCommunication

class Direction(Enum):
    Forward = 0
    Backward = 1

class MagnetDirection(Enum):
    Enforce = 1
    Release = 0

class ICInterface:

    # IM to IC ids
    CMD_INIT_TELE = 1
    CMD_DRIVE_DISTANCE = 2
    CMD_DRIVE_JOG = 3
    CMD_DRIVE_TO_END = 4
    CMD_MOVE_TELE = 5
    CMD_ENABLE_MAGNET = 6
    CMD_DISABLE_MAGNET = 7

    # IC to IM ids
    CMD_END_INIT_TELE = 8
    CMD_END_DRIVE = 9
    CMD_EMD_MOVE_TELE = 10
    CMD_POSITION_FEEDBACK = 11
    CMD_END_RUN = 12

    def __init__(self):
        self.ic_com = ICCommunication()
        self.ic_com.register_callback(self.ic_callback)
        self.callback_once = defaultdict(list)
        self.callback_permanent = defaultdict(list)

        # start ic communication
        self.ic_com.start()

    # send Commands
    def init_tele(self, timeout: float=None):
        self.ic_com.send_msg(self.CMD_INIT_TELE)
        self._wait_for_ic_callback(self.CMD_END_INIT_TELE, timeout)

    def init_tele_async(self, callback, timeout: float=None):
        raise NotImplementedError()

    def register_position_callback(self, callback: Callable[[int, int], None]):
        self.callback_permanent[self.CMD_POSITION_FEEDBACK].append(callback)

    def unregister_position_callback(self, callback):
        self.callback_permanent[self.CMD_POSITION_FEEDBACK].remove(callback)

    def move_tele_async(self, distance: int, direction: Direction, callback):
        payload = distance.to_bytes(2, byteorder='big')
        payload += direction.value.to_bytes(1, byteorder='big')

        self.ic_com.send_msg(self.CMD_MOVE_TELE, payload)
        self.callback_once[self.CMD_EMD_MOVE_TELE].append(callback)

    def drive_distance_async(self, distance: int, speed: chr,
                             direction: Direction, callback):
        payload = distance.to_bytes(2, byteorder='big')
        payload += speed.to_bytes(1, byteorder='big')
        payload += direction.value.to_bytes(1, byteorder='big')

        self.ic_com.send_msg(self.CMD_DRIVE_DISTANCE, payload)
        self.callback_once[self.CMD_END_DRIVE]\
            .append(callback)

    def drive_jog(self, speed: int, direction: Direction):
        payload = speed.to_bytes(1, byteorder='big')
        payload += direction.value.to_bytes(1, byteorder='big')

        self.ic_com.send_msg(self.CMD_DRIVE_JOG, payload)

    def enable_magnet(self, direction: MagnetDirection):
        payload = direction.value.to_bytes(1, byteorder='big')

        self.ic_com.send_msg(self.CMD_ENABLE_MAGNET, payload)

    def drive_to_end_async(self, predicted_distance: int, speed: int, direction: Direction, callback):
        payload = predicted_distance.to_bytes(2, byteorder='big')
        payload += speed.to_bytes(1, byteorder='big')
        payload += direction.value.to_bytes(1, byteorder='big')

        self.ic_com.send_msg(self.CMD_DRIVE_TO_END, payload)
        self.callback_once[self.CMD_END_RUN] \
            .append(callback)

    def _wait_for_ic_callback(self, cmd_id: int, timeout: float):
        thread_event = Event()
        self.callback_once[cmd_id].append(lambda: thread_event.set())
        timeout = not thread_event.wait(timeout)
        if timeout:
            raise Exception('Not received callback within timeout: CMD_ID {}, timeout {}'.format(cmd_id, timeout))

    def ic_callback(self, cmd_id: int, payload: List[chr]):
        parameters = self._extract_parameters(cmd_id, payload)
        if cmd_id in self.callback_once:
            for callback in self.callback_once.pop(cmd_id):
                callback(*parameters)

        if cmd_id in self.callback_permanent:
            for callback in self.callback_permanent[cmd_id]:
                callback(*parameters)

    def _extract_parameters(self, cmd_id: int, payload: bytes):
        if cmd_id == self.CMD_POSITION_FEEDBACK:
            x_position = int.from_bytes(payload[:2], 'big')
            z_position = int.from_bytes(payload[2:4], 'big')
            return [x_position, z_position]
        else:
            return []





