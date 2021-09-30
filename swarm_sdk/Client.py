from swarm_sdk.SwarmUtils import NetUtils
from typing import List

import time
import threading
import struct
import serial
import cv2



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

        # Отправка стартового сообщения
        self.send_message(message=self.create_message_Start_Communication(), destination=('localhost', 8000))

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
                self.server_message.append(data)  # сохраняем полученное сообщение в список
                self.message_handler()
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

    # отправить сообщение по юарту
    def send_message_uart(self, message):
        self.uart.write(message)
        pass

    ###################################
    # Блок анализа принятых сообщений #
    ###################################
    def message_handler(self):
        # while True:
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
                self.send_message_uart(message=self.create_message_COPTER_ARM())

            elif type_message == "CL":
                """выполнить посадку"""
                print("Получено сообщение CL")
                self.send_message_uart(message=self.create_message_COPTER_LAND())

            elif type_message == "CD":
                """выполнить посадку"""
                print("Получено сообщение CD")
                self.send_message_uart(message=self.create_message_COPTER_DISARM())

            elif type_message == "MR":
                """выполнить сброс груза"""
                print("Получено сообщение MR")

            # Если пришли новые координаты для коптера
            elif type_message == 'NC':
                __, __, X, Y, Z, __ = struct.unpack(">2cfff1c", message)
                # отправляем по юарту координаты и меняем состояние коптера
                print("Получено сообщение NC", X, Y, Z)
                self.condition = "Moving"
                #self.send_message_uart(message=self.create_message_New_Coordinates(X, Y, Z))

                ### ДЛЯ ТЕСТА!!!!! ОБЯЗАТЕЛЬНО УДАЛИТЬ!!!!!!!!!! ###
                time.sleep(3)
                print("Выполнено")
                self.condition = "Waiting"
                self.send_message(('localhost', 8000), self.create_message_Task_Completed())
                ####################################################

            elif type_message == 'SL':
                __, __, R, G, B, __ = struct.unpack(">2cfff1c", message)
                # отправляем по юарту команду и меняем состояние коптера
                print("Получено сообщение SL", R, G, B)
                self.send_message_uart(message=self.create_message_Set_Leds(R, G, B))

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
                self.send_message(message=self.create_message_Copter_Coordinates(X, Y, Z))

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