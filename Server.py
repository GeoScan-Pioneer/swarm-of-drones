import socket
import threading
import time
import cv2
import numpy as np
import struct


# Ужасная карта ради карты.
# !!! сделать менее прожерливую карту !!! #
class Card():
    def __init__(self):
        self.card = np.zeros((512,512,3), np.uint8)
        # Draw a diagonal blue line with thickness of 5 px
        #cv2.line(self.card, (0, 0), (511, 511), (255, 255, 255), 5)

        self.copter = []
        self.coord = []

    def image_point(self):
        while True:
            if len(self.copter) > 0:
                self.card = np.zeros((512, 512, 3), np.uint8)
                for i in range (len(self.copter)):
                    x = (512 / 10) * float(self.coord[i][0])
                    y = (512 / 10) * float(self.coord[i][1])
                    cv2.circle(self.card, (int(x), int(y)), 2, (255, 255, 255), -1)
                #print(1)
                cv2.imshow("Card", self.card)
                key = cv2.waitKey(10)
                if key == 27:
                    break


class Copter():
    def __init__(self, num_copter):
        self.num_copter = num_copter
        self.coordinates_copter = [None, None, None]
        self.addr = [None, None]
        self.condition = None


class Server():
    def __init__(self, id, port, card):
        self.id_server = id
        self.port_server = port

        self.serv_sock = None
        self.clients = [] # список клиентов
        self.cid = 0


        # список сообщений от клиентов и самих клиентов
        self.clients_message = []

        self.card = card

    def run_server_UDP(self):
        self.serv_sock = self.__create_serv_sock_UDP()  # создание сервера
        t1 = threading.Thread(target=self.message_handler, args=())  # запуск потока обработки сообщений
        t1.start()

        t2 = threading.Thread(target=self.test_message, args=())  # запуск потока обработки сообщений
        t2.start()

        while True:
            data, client_addr = self.serv_sock.recvfrom(1024)
            self.clients_message.append(data)
            self.clients_message.append(client_addr)


    def __create_serv_sock_UDP(self):
        serv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        serv_sock.bind((self.id_server, self.port_server))
        return serv_sock

    # отлдельный поток для приема сообщений от нового клиента
    def accept_message_client(self, client_sock, cid):
        while True:
            request = client_sock.recv(1024)
            print(request)
            self.clients_message.append(request)  # запись всех полученных сообщений в список

    def handler_card(self):
        self.card.image_point()

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
    def message_handler(self):

        while True:
            # ---------------------------------------
            # Если есть принятое сообщение от клиента
            # ---------------------------------------
            if len(self.clients_message) > 0:

                # считываем сообщение и клиента, удаляем его и определяем его тип
                message = self.clients_message.pop(0)
                client = self.clients_message.pop(0)

                type_message = self.message_parser2(message)

                # если пришло стартовое то запоминаем клиента
                if type_message == "SC":
                    self.clients.append(client)



                # Если пришли координаты
                elif type_message == "CC":
                    __, __, X, Y, Z, __ = struct.unpack(">2cfff1c", message)
                    print(X, Y, Z)


    #########################
    # Блок тестовых функций #
    #########################

    def test_message(self):
        while True:
            if len(self.clients) > 0:
                self.send_message(client=self.clients[0], message=self.create_message_CA())
                time.sleep(2)

                self.send_message(client=self.clients[0], message=self.create_message_CL())
                time.sleep(2)

                self.send_message(client=self.clients[0], message=self.create_message_CD())
                time.sleep(2)

                self.send_message(client=self.clients[0], message=self.create_message_NC(10.30, 49.33, 1.00))
                time.sleep(2)

                self.send_message(client=self.clients[0], message=self.create_message_SL(0.30, 0.33, 1.00))










if __name__ == '__main__':
    card = Card()
    server = Server(id="127.0.0.1", port=8000, card=card)
    server.run_server_UDP()
