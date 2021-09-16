import socket
#import picamera
import threading
import serial
import time
import cv2
import numpy as np
import struct



class Client():
    def __init__(self, id, port, ind_copter, port_uart='COM1', boud_uart=9600, timeout_uart=1):
        # Параметры дял сокета
        self.id_server = id
        self.port_server = port
        self.ind_copter = ind_copter
        self.serv_sock = None

        # список полученных сообщений. Выполненное сообщение удаляется
        self.server_message = []
        self.uart_message = []

        # Текущие состояние: Wait, Flight, Arm, Search
        self.condition = "Wait"

        # массив хранения текущих координат коптера
        self.coordinates = [0, 0, 0]
        # координаты дома (берутся при взлете)
        self.home = [0,0,0]

        try:
            # Параметры для юарта
            self.uart = serial.Serial(port_uart, boud_uart, timeout=timeout_uart)
            self.uart.flush()  # очистка юарта
        except:
            print("Не удалось подключиться к ЮАРТУ")


        # Параметры для поиска aruco
        self.DICTIONARY = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
        self.PARAMETERS = cv2.aruco.DetectorParameters_create()


    def run_server_UDP(self):
        self.serv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=0)
        self.serv_sock.bind(("localhost", 8001))
        self.serv_sock.setblocking(0) # отключение блокировки сервера при приеме сообщений

        # Отправка стартового сообщения
        self.send_message_server(message=self.create_message_SC())


        # Обрабатываем сообщения в отдельном потоке
        stream_for_messages_handler = threading.Thread(target=self.message_handler, args=())
        stream_for_messages_handler.start()

        while True:
            # принять сообщение из юарта
            self.accepting_messages_uart()

            # принять сообщение от сервера
            self.accepting_messages()

        pass



    # В отдельном потоке принимаем сообщения
    def accepting_messages(self):
        try:
            # считываем полученное сообщение
            data, __ = self.serv_sock.recvfrom(100)
            self.server_message.append(data)  # сохраняем полученное сообщение в список
        except:
            pass


    # Принять сообщение из арта
    def accepting_messages_uart(self):
        if self.uart.in_waiting > 0:
            data = self.uart.readline()
            self.uart_message.append(data)
            print(1)

    ###################################################
    # Блок отправления,создания и обработки сообщений #
    ###################################################
    # отправить сообщение на сервер
    def send_message_server(self, message):
        self.serv_sock.sendto(message, (self.id_server, self.port_server))

    # Start Communication
    def create_message_SC(self):
        return struct.pack(">2sh1c", b'SC', self.ind_copter, b"\n")
    # координаты коптера для отправки на сервер
    def create_message_CC(self, X, Y, Z):
        return struct.pack(">2shfff1c", b'CC', self.ind_copter, X, Y, Z, b"\n")


    # Сообщения для отправки на коптер по UART
    # New Coordinates
    def create_message_NC_UART(self, X, Y, Z):
        return struct.pack(">2sfff1c", b'NC', X, Y, Z, b"\n")

    # Set Leds
    def create_message_SL_UART(self, R, G, B):
        return struct.pack(">2sfff1c", b'SL', R, G, B, b"\n")

    # Copter ARM
    def create_message_CA_UART(self):
        return struct.pack(">2sfff1c", b'CA', 0, 0, 0, b"\n")

    # Copter ARM
    def create_message_CL_UART(self):
        return struct.pack(">2sfff1c", b'CL', 0, 0, 0, b"\n")

    # Copter DISARM
    def create_message_CD_UART(self):
        return struct.pack(">2sfff1c", b'CD', 0, 0, 0, b"\n")


    # Первые два байта сообщения всегда будут буквенными и содержать смысл последующей команды.
    # Например NC - новые координаты
    def message_parser2(self, message):
        type_message = message[0:2].decode("utf-8")
        return type_message

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
                type_message = self.message_parser2(message)
                # команда ARM
                if type_message == 'CA':
                    """выполнить предстартовую подготовку"""
                    print("Получено сообщение CA")
                    self.send_message_uart(message=self.create_message_CA_UART())

                elif type_message == "CL":
                    """выполнить посадку"""
                    print("Получено сообщение CL")
                    self.send_message_uart(message=self.create_message_CL_UART())

                elif type_message == "CD":
                    """выполнить посадку"""
                    print("Получено сообщение CD")
                    self.send_message_uart(message=self.create_message_CD_UART())

                elif type_message == "MR":
                    """выполнить сброс груза"""
                    print("Получено сообщение MR")

                # Если пришли новые координаты для коптера
                elif type_message == 'NC':
                    __, __, X, Y, Z, __ = struct.unpack(">2cfff1c", message)
                    # отправляем по юарту координаты и меняем состояние коптера
                    print("Получено сообщение NC", X, Y, Z)
                    self.condition = "Flight"
                    self.send_message_uart(message=self.create_message_NC_UART(X, Y, Z))

                elif type_message == 'SL':
                    __, __, R, G, B, __ = struct.unpack(">2cfff1c", message)
                    # отправляем по юарту команду и меняем состояние коптера
                    print("Получено сообщение SL", R, G, B)
                    self.send_message_uart(message=self.create_message_SL_UART(R, G, B))


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
                type_message = self.message_parser2(message)

                # Если сообщение с координатами, то определяем их и отправляем на сервер
                if type_message == "CC":
                    __, __, X, Y, Z, __ = struct.unpack(">2cfff1c", message)

                    # Генерируем сообщение
                    self.send_message_server(message=self.create_message_CC(X, Y, Z))

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




if __name__ == '__main__':
    client = Client(id="127.0.0.1", port=8000, ind_copter=0, port_uart="COM1")
    client.run_server_UDP()
    pass
