import socket
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from typing import List, Callable

from mgmt_utils.generic import Generic


class UICommunication:

    def __init__(self):
        self.server_socket = None
        self.listen_thread = None
        self.is_listening = False
        self.clients = []

        # callbacks
        self.callbacks = []
        self.callback_thread_pool = ThreadPoolExecutor()

    def start(self, ip_address: str='0.0.0.0', port: int=5006):
        self.stop()

        # start listen
        self.is_listening = True
        self.listen_thread = Thread(target=self._listen, args=(ip_address, port))
        self.listen_thread.start()

    def register_callback(self, callback: Callable[[int, List[chr]], None]):
        self.callbacks.append(callback)

    def send_msg(self, data):
        i = 0
        while i < len(self.clients):
            payload = data.encode('utf-8')
            if len(payload) > 99999:
                raise Exception('Payload is longer than protocol supports')
            length = '{:0>5}'.format(len(payload)).encode('utf-8')
            try:
                self.clients[i].conn.send(length + payload)
                i += 1
            except Exception as ex:
                client = self.clients[i]
                self.clients.remove(client)
                print("Not able to send to client: {}".format(client.address))
                client.conn.shutdown(socket.SHUT_RDWR)
                client.conn.close()
                print("Client {} removed from distribution list".format(client.address))

    def stop(self):
        if self.listen_thread:
            self.is_listening = False
            self.listen_thread.join()
            self.listen_thread = None
            self.server_socket = None

    def _listen(self, ip_address: str, port: int):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.settimeout(10)
        self.server_socket.bind((ip_address, port))
        self.server_socket.listen(5)  # defines max connect requests

        while self.is_listening:
            try:
                conn, address = self.server_socket.accept()
                receive_thread = Thread(target=self._receive, args=(conn,))
                receive_thread.start()
                self.clients.append(Generic(conn=conn, receive_thread=receive_thread, address=address))
                print("Client {} connected to Richi Bahn\n".format(address))
            except Exception as ex:
                if ex.args and ex.args[0] == 'timed out':
                    pass # ignore time out exception
                else:
                    raise ex

    def _receive(self, conn):
        while True:
            payload = conn.recv(5)
            if payload == b'':
                raise RuntimeError("socket connection broken")
            msg_length = int(payload.decode("utf-8"))
            payload = conn.recv(msg_length)
            if payload == b'':
                raise RuntimeError("socket connection broken")
            self._on_receive(payload)

    def _on_receive(self, payload):
        payload = payload.decode("utf-8")
        cmd_id = int(payload[0])
        data = payload[1:]

        for callback in self.callbacks:
            future = self.callback_thread_pool.submit(callback, cmd_id, data)
            future.add_done_callback(lambda x: x.result())
