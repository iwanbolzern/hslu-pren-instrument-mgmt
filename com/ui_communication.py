import socket
from threading import Thread

from utils.generic import Generic


class UICommunication:

    def __init__(self):
        self.server_socket = None
        self.listen_thread = None
        self.is_listening = False
        self.clients = []

    def start(self, ip_address: str='', port: int=5006):
        self.stop()

        # start listen
        self.is_listening = True
        self.listen_thread = Thread(target=self._listen, args=(ip_address, port))
        self.listen_thread.start()

    def send_position(self, x, y):
        self._send_msg('1{},{}'.format(x, y))

    def send_log(self, log_msg):
        self._send_msg('2{}'.format(log_msg))

    def _send_msg(self, data):
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
                print("Not able to send to client: {}".format(self.clients[i].address))
                self.clients[i].conn.shutdown(socket.SHUT_RDWR)
                self.clients[i].conn.close()
                print("Client {} removed from distribution list".format(self.clients[i].address))
                self.clients.remove(self.clients[i])


    def stop(self):
        if self.listen_thread:
            self.is_listening = False
            self.listen_thread.join()
            self.listen_thread = None
            self.server_socket = None

    def _listen(self, ip_address: str, port: int):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.settimeout(10)
        self.server_socket.bind((ip_address, port))
        self.server_socket.listen(5)  # defines max connect requests

        while self.is_listening:
            try:
                conn, address = self.server_socket.accept()
                receive_thread = Thread(target=self._receive, args=(conn,))
                receive_thread.start()
                self.clients.append(Generic(conn=conn, receive_thread=receive_thread, address=address))
                print("Client {} connected to live stream\n".format(address))
            except Exception as ex:
                if ex.args and ex.args[0] == 'timed out':
                    pass # ignore time out exception
                else:
                    raise ex


    def _receive(self, conn):
        pass