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
        self.serial_thread = Thread(target=self._serial_handle, args=(self.stop_event,))
        self.serial_thread.start()

    def register_callback(self, callback: Callable[int, List[chr]]):
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
            self.callback_thread_pool.submit(callback, (cmd_id, data))

    def send_msg(self, cmd_id: int, data: List[chr]=[]):
        cmd_byte = chr(cmd_id)
        msg = [cmd_byte] + data
        self.message_queue.put(msg)

    def _serial_handle(self):
        # init serial port
        self.serial = serial.Serial(
            port='/dev/ttyAMA0',
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1)

        while not self.stop_event.is_set():
            while not self.message_queue.empty():
                msg = self.message_queue.get()
                self.serial.write(msg)

            while self.serial.inWaiting() >= 2:
                length = self.serial.read(2)
                payload = self.serial.read(length)
                self._on_receive(payload)

            time.sleep(0.1)