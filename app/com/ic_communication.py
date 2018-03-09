import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Event, Thread
from typing import List, Callable

import serial

class ICCommunication:

    def __init__(self):
        self.serial = None
        self.stop_event = None
        self.serial_thread = None
        self.callbacks = []
        self.callback_thread_pool = ThreadPoolExecutor()

    def start(self):
        self.stop()

        # start listen
        self.stop_event = Event()
        self.message_queue = Queue()
        self.serial_thread = Thread(target=self._serial_handle)
        self.serial_thread.start()

    def register_callback(self, callback: Callable[[int, List[chr]], None]):
        self.callbacks.append(callback)

    def stop(self):
        if self.serial_thread:
            self.stop_event.set()
            self.serial_thread.join()
            self.serial = None
            self.serial_thread = None
            self.stop_event = None

    def _on_receive(self, payload: List[chr]):
        cmd_id = payload[0]
        data = payload[1:]

        for callback in self.callbacks:
            future = self.callback_thread_pool.submit(callback, cmd_id, data)
            future.add_done_callback(lambda x: x.result())

    def send_msg(self, cmd_id: int, data: bytes=b''):
        cmd_byte = cmd_id.to_bytes(1, 'big')
        msg = cmd_byte + data
        self.message_queue.put(msg)

    def _serial_handle(self):
        # init serial port
        self.serial = serial.Serial(
            port='COM5',
            baudrate=38400,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1)

        while True:
            self.serial.write(int(1).to_bytes(2, 'big'))

        while not self.stop_event.is_set():
            while not self.message_queue.empty():
                msg = self.message_queue.get()
                self.serial.write(len(msg).to_bytes(2, 'big') + msg)

            while self.serial.inWaiting() >= 2:
                length = self.serial.read(2)
                length = int.from_bytes(length, byteorder='big')
                payload = self.serial.read(length)
                self._on_receive(payload)

            time.sleep(0.1)