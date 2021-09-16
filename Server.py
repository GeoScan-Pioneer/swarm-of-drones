import socket
import threading
import time
import cv2
import numpy as np
import struct

from typing import List


class Copter():
    def __init__(self, num_copter, addr):
        self.num_copter = num_copter
        self.coordinates_copter = [(0, 0), 0]
        self.addr = addr
        self.condition = None


class Server():
    """ Сервер """
    def __init__(self, id, port, number=4):
        self.id_server = id
        self.port_server = port

        self.serv_sock = None
        self.clients: List[Copter] = [] # список клиентов
        self.cid = 0

        # список сообщений от клиентов
        self.clients_message = []

    def run_server_UDP(self):
        self.serv_sock = self.__create_serv_sock_UDP()  # создание сервера

        t2 = threading.Thread(target=self.test_message, args=())  # запуск тестовой функции
        t2.start()

        while True:
            # принимаем все сообщения. После приема сообщение и клиент записываются в список
            data, client_addr = self.serv_sock.recvfrom(100)

            self.message_handler2(data, client_addr)




    def __create_serv_sock_UDP(self):
        serv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        serv_sock.bind((self.id_server, self.port_server))
        return serv_sock


    #########################################
    # Блок отправления и создания сообщений #
    #########################################
    # отправить сообщение
    def send_message(self, client, message):
        self.serv_sock.sendto(message, client)

    # Magnet Reset
    def create_message_MR(self):
        return struct.pack(">2s1c", b'MR', b"\n")

    # COPTER_LAND
    def create_message_CL(self):
        return struct.pack(">2s1c", b'CL', b"\n")

    # COPTER_ARM
    def create_message_CA(self):
        return struct.pack(">2s1c", b'CA', b"\n")

    # COPTER_DISARM
    def create_message_CD(self):
        return struct.pack(">2s1c", b'CD', b"\n")

    # New Coordinates + X + Y + Z
    def create_message_NC(self, X, Y, Z):
        return struct.pack(">2sfff1c", b'NC', X, Y, Z, b"\n")

    # Set Leds
    def create_message_SL(self, R, G, B):
        return struct.pack(">2sfff1c", b'SL', R, G, B, b"\n")

    # Search in area. Предаются координаты двух точек прямоугольника
    def create_message_SA(self, X1, Y1, X2, Y2):
        return struct.pack(">2sffff1c", b'SA', X1, Y1, X2, Y2, b"\n")

    # Search in pont. Предаются координаты точки
    def create_message_SP(self, X, Y, Z):
        return struct.pack(">2sfff1c", b'SP', X, Y, Z, b"\n")


    # разбираем пришедшее сообщение
    def message_parser2(self, message):
        type_message = message[0:2].decode("utf-8")
        return type_message


    ###################################
    # Блок анализа принятых сообщений #
    ###################################
    def message_handler2(self, message, client_addr):

        type_message = self.message_parser2(message)

        # если пришло стартовое то запоминаем клиента
        if type_message == "SC":
            __, ind_copter, __ = struct.unpack(">2sh1c", message)

            # Создаем экземпляр класса Copter
            client = Copter(num_copter=self.cid, addr=client_addr)
            self.clients.append(client)
            print(self.clients[self.cid].addr)
            self.cid = self.cid + 1

        # Если пришли координаты
        elif type_message == "CC":
            __, ind_copter, X, Y, Z, __ = struct.unpack(">2shfff1c", message)

            print(X, Y, Z)



    #########################
    # Блок тестовых функций #
    #########################

    def test_message(self):
        while True:
            if len(self.clients) > 0:
                self.send_message(client=self.clients[0].addr, message=self.create_message_CA())
                time.sleep(2)

                self.send_message(client=self.clients[0].addr, message=self.create_message_CL())
                time.sleep(2)

                self.send_message(client=self.clients[0].addr, message=self.create_message_CD())
                time.sleep(2)

                self.send_message(client=self.clients[0].addr, message=self.create_message_NC(10.30, 49.33, 1.00))
                time.sleep(2)

                self.send_message(client=self.clients[0].addr, message=self.create_message_SL(0.30, 0.33, 1.00))

                time.sleep(2)


if __name__ == '__main__':
    server = Server(id="127.0.0.1", port=8000)
    server.run_server_UDP()
    print(1)