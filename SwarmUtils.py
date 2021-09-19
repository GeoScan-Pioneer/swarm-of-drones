import socket
import threading
import time
import cv2
import numpy as np
import struct
import serial

import matplotlib.pyplot as plt
import tkinter as tk

from typing import List


class Card(threading.Thread):
    """ Класс отвечающий за карту """
    # height, width - размеры предполагаемой карты в метрах
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def callback(self):
        self.window.quit()

    def run(self):
        self.window = tk.Tk()
        self.window.title("Live map")
        self.window['bg'] = 'white'
        self.window.resizable(width=False, height=False)
        self.window.config(padx=10, pady=10)
        self.window.geometry('600x600')

        self.canvas = tk.Canvas(self.window)
        self.canvas.pack(fill=tk.BOTH, expand=True)


        self.copter_radius = 10
        self.copter_area_radius = 30

        self.window.mainloop()

    def add_copter(self):
        oval1 = self.canvas.create_oval(300-self.copter_area_radius/2,
                                        300-self.copter_area_radius/2,
                                        300+self.copter_area_radius/2,
                                        300+self.copter_area_radius/2,
                                        outline="#FFAAAA", fill="#FFDDDD")
        oval2 = self.canvas.create_oval(300-self.copter_radius/2,
                                        300-self.copter_radius/2,
                                        300+self.copter_radius/2,
                                        300+self.copter_radius/2,
                                        outline="#FF0000", fill="#FF0000")
        return oval1, oval2


class Copter:
    def __init__(self, num_copter, addr, visual):
        self.num_copter = num_copter
        self.coordinates_copter = [(0, 0), 0]
        self.addr = addr
        self.condition = None
        self.visual = visual

class NetUtils:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        #self.socket.settimeout(1)
        self.socket.setblocking(0)  # отключение блокировки при приеме сообщений

        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.bind((ip, port))

    #########################################
    # Блок отправления и создания сообщений #
    #########################################

    # отправить сообщение
    def send_message(self, destination, message):
        self.socket.sendto(message, destination)

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
    def message_parser(self, message):
        type_message = message[0:2].decode("utf-8")
        return type_message


class Server(NetUtils):
    """ Сервер """
    def __init__(self, ip_server, port_serer, card, number=4):
        super().__init__(ip=ip_server, port=port_serer)

        self.clients: List[Copter] = [] # список клиентов
        self.cid = 0

        self.card = card

        # список сообщений от клиентов
        self.clients_message = []

    def run_UDP(self):

        # Принимаем сообщения от сервера в отдельном потоке
        stream_for_messages = threading.Thread(target=self.accepting_messages, args=())
        stream_for_messages.daemon = True
        stream_for_messages.start()



     # В отдельном потоке принимаем сообщения
    def accepting_messages(self):
        while True:
            try:
                # принимаем все сообщения. После приема сообщение и клиент записываются в список
                data, client_addr = self.socket.recvfrom(100)
                print("Received ", data, " from ", client_addr)
                self.message_handler(data, client_addr)
            except:
                pass



    ###################################
    # Блок анализа принятых сообщений #
    ###################################
    def message_handler(self, message, client_addr):
        type_message = self.message_parser(message)
        # если пришло стартовое то запоминаем клиента

        if type_message == "SC":
            # Создаем экземпляр класса Copter
            client = Copter(num_copter=self.cid, addr=client_addr, visual=self.card.add_copter())
            self.clients.append(client)
            print(self.clients[self.cid].addr)
            self.cid = self.cid + 1

        # Если пришли координаты
        elif type_message == "CC":
            __, X, Y, Z, __ = struct.unpack(">2sfff1c", message)
            client = self.get_client_by_address(client_addr)
            client = self.get_client_by_id(-1)
            self.card.canvas.moveto(client.visual[0], X+self.card.copter_radius/2, Y+self.card.copter_radius/2)
            self.card.canvas.moveto(client.visual[1], X+self.card.copter_area_radius/2, Y+self.card.copter_area_radius/2)
            print(X, Y, Z)



    def get_client_by_address(self, addr):
        for client in self.clients:
            if client.addr == addr:
                return client
        else:
            return None

    def get_client_by_id(self, id):
        return self.clients[id]

    ###################################
    ###### Алгоритмы управления #######
    ###################################

    # вычисляет дистанцию между всеми коптерами и возвращает длину и пару коптеров, которые ближе допустимого расстояния
    def __dist(self, p1, p2):
        return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

    def check_min_distance(self):
        distances = []
        for i in range(len(self.clients)):
            for j in range(i + 1, len(self.clients)):
                dist = self.__dist(self.clients[i].coordinates_copter[0], self.clients[j].coordinates_copter[0])
                if dist <= 1:
                    distances.append((i, j, dist))
        return distances


    #########################
    # Блок тестовых функций #
    #########################

    def test_message(self):
        while True:
            if len(self.clients) > 0:
                self.send_message(destination=self.clients[0].addr, message=self.create_message_CA())
                time.sleep(2)

                self.send_message(destination=self.clients[0].addr, message=self.create_message_CL())
                time.sleep(2)

                self.send_message(destination=self.clients[0].addr, message=self.create_message_CD())
                time.sleep(2)

                self.send_message(destination=self.clients[0].addr, message=self.create_message_NC(10.30, 49.33, 1.00))
                time.sleep(2)

                self.send_message(destination=self.clients[0].addr, message=self.create_message_SL(0.30, 0.33, 1.00))

                time.sleep(2)


class Client(NetUtils):
    def __init__(self, ip, port, ip_server="localhost", port_server=8000, port_uart='COM1', boud_uart=9600, timeout_uart=1):
        super().__init__(ip=ip, port=port)
        # Параметры дял сокета
        self.ip_server = ip_server
        self.port_server = port_server

        # список полученных сообщений. Выполненное сообщение удаляется
        self.server_message = []
        self.uart_message = []

        # Текущие состояние: Waiting, Moving, Armed, Landed
        self.condition = "Waiting"

        # массив хранения текущих координат коптера
        self.coordinates = [0, 0, 0]
        # координаты дома (берутся при взлете)
        self.home = [0, 0, 0]

        try:
            # Параметры для юарта
            self.uart = serial.Serial(port_uart, boud_uart, timeout=timeout_uart)
            self.uart.flush()  # очистка юарта
        except:
            self.uart = None
            print("Не удалось подключиться к ЮАРТУ")

        # Параметры для поиска aruco
        self.DICTIONARY = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
        self.PARAMETERS = cv2.aruco.DetectorParameters_create()

    def run_UDP(self):
        # Принимаем сообщения от сервера в отдельном потоке
        stream_for_messages = threading.Thread(target=self.accepting_messages, args=())
        stream_for_messages.daemon = True
        stream_for_messages.start()


    # В отдельном потоке принимаем сообщения
    def accepting_messages(self):
        while True:
            # Принимаем сообщение из юарта
            try:
                self.accepting_messages_uart()
            except:
                #print("ошибка приема сообщения из юарта")
                pass

            # Принимаем сообщение от сервера
            try:
                # считываем полученное сообщение
                data, __ = self.socket.recvfrom(100)
                self.message_handler()
                self.server_message.append(data)  # сохраняем полученное сообщение в список
            except:
                #print("Ошибка приема сообщений от сервера")
                pass



    # Принять сообщение из юарта
    def accepting_messages_uart(self):
        if self.uart is not None and self.uart.in_waiting > 0:
            data = self.uart.readline()
            self.uart_message.append(data)

    ###################################################
    # Блок отправления,создания и обработки сообщений #
    ###################################################

    # Start Communication
    def create_message_SC(self):
        return struct.pack(">2s1c", b'SC', b"\n")

    # координаты коптера для отправки на сервер
    def create_message_CC(self, X, Y, Z):
        return struct.pack(">2sfff1c", b'CC', X, Y, Z, b"\n")

    # отправить сообщение по юарту
    def send_message_uart(self, message):
        self.uart.write(message)
        pass

    ###################################
    # Блок анализа принятых сообщений #
    ###################################
    def message_handler(self):
        while True:
            # ---------------------------------------
            # Если есть принятое сообщение от сервера
            # ---------------------------------------
            if len(self.server_message) > 0:
                # считываем сообщение, удаляем его и определяем его тип
                message = self.server_message.pop(0)
                type_message = self.message_parser(message)
                # команда ARM
                if type_message == 'CA':
                    """выполнить предстартовую подготовку"""
                    print("Получено сообщение CA")
                    self.send_message_uart(message=self.create_message_CA())

                elif type_message == "CL":
                    """выполнить посадку"""
                    print("Получено сообщение CL")
                    self.send_message_uart(message=self.create_message_CL())

                elif type_message == "CD":
                    """выполнить посадку"""
                    print("Получено сообщение CD")
                    self.send_message_uart(message=self.create_message_CD())

                elif type_message == "MR":
                    """выполнить сброс груза"""
                    print("Получено сообщение MR")

                # Если пришли новые координаты для коптера
                elif type_message == 'NC':
                    __, __, X, Y, Z, __ = struct.unpack(">2cfff1c", message)
                    # отправляем по юарту координаты и меняем состояние коптера
                    print("Получено сообщение NC", X, Y, Z)
                    self.condition = "Flight"
                    self.send_message_uart(message=self.create_message_NC(X, Y, Z))

                elif type_message == 'SL':
                    __, __, R, G, B, __ = struct.unpack(">2cfff1c", message)
                    # отправляем по юарту команду и меняем состояние коптера
                    print("Получено сообщение SL", R, G, B)
                    self.send_message_uart(message=self.create_message_SL(R, G, B))

                elif type_message == 'SA':
                    __, __, X1, Y1, X2, Y2, __ = struct.unpack(">2sffff1c", message)
                    self.condition = "Search"
                    pass

            # -------------------------------------
            # Если есть принятое сообщение из юарта
            # -------------------------------------
            if len(self.uart_message) > 0:
                # считываем сообщение и удаляем его
                message = self.uart_message.pop(0)
                type_message = self.message_parser(message)

                # Если сообщение с координатами, то определяем их и отправляем на сервер
                if type_message == "CC":
                    print(1)
                    __, __, X, Y, Z, __ = struct.unpack(">2cfff1c", message)

                    # Генерируем сообщение
                    # self.send_message_server(message=self.create_message_CC(X, Y, Z))

    ###################################
    ###### Алгоритмы управления #######
    ###################################
    # полет по области с поиском маркеров
    def search_markers_in_area(self, x1, y1, x2, y2, z):
        """Генерация траектории для полета внутри прямоугольника и поиска маркера"""
        pass


    # полет в точку и поиск в ней маркеров
    def search_markers_in_point(self, x, y, z):
        """Генерация траектории для полета в точку и поиска маркера"""
        pass

    # Поиск маркера на кадре
    def find_markers(self, frame):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray_frame, self.DICTIONARY,
                                                                  parameters=self.PARAMETERS)
        if ids is None:
            return None
        return ids