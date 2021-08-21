import socket
# import picamera
import threading
import serial
import time


class Client():
    def __init__(self, id, port, ind_copter):
        self.id_server = id
        self.port_server = port
        self.ind_copter = ind_copter

        self.serv_sock = None
        self.server_message = []

    def run_server(self):
        self.serv_sock = self.__create_serv_sock()
        stream_for_messages = threading.Thread(target=self.accepting_messages, args=())  # запуск потока обработки сообщений
        stream_for_messages.start()

        stream_for_messages_handler = threading.Thread(target=self.message_handler, args=())  # запуск потока обработки сообщений
        stream_for_messages_handler.start()

        while True:
            self.send_message(self.create_message_CC(X=10.30, Y=20.00, Z=1.22))
            time.sleep(1)

    # Создать соккет и соединились с сервером
    def __create_serv_sock(self):
        serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
        serv_sock.connect((self.id_server, self.port_server))
        print("Успешное соединение")
        return serv_sock

    # В отдельном потоке принимаем сообщения
    def accepting_messages(self):
        while True:
            data = self.serv_sock.recv(1024).decode("utf8")  # считываем полученное сообщение и декодируем
            self.server_message.append(data)  # сохраняем полученное сообщение

    #########################################
    # Блок отправления и создания сообщений #
    #########################################
    def send_message(self, message):
        self.serv_sock.sendall(message)

    def create_message_H(self):
        return "HC".encode("utf8")

    def create_message_CC(self, X, Y, Z):
        message = str(self.ind_copter) + "CC" "X" + str(X) + "Y" + str(Y) + "Z" + str(Z)
        return message.encode("utf8")

    # разбираем пришедшее сообщение
    def message_parser(self, message):
        type_message = message[0:2]
        message = message[2:len(message)]
        return type_message, message

    ###################################
    # Блок анализа принятых сообщений #
    ###################################
    def message_handler(self):
        while True:
            # Если есть принятое сообщение
            if len(self.server_message) > 0:

                # считываем сообщение и удаляем его
                message = self.server_message.pop(0)
                type_message, message = self.message_parser(message)

                # Если пришли координаты
                if type_message == 'NC':
                    ind_X = message.find("X")
                    ind_Y = message.find("Y")
                    ind_Z = message.find("Z")
                    x = "{:.2f}".format(float(message[(ind_X + 1):(ind_Y)]))
                    y = "{:.2f}".format(float(message[(ind_Y + 1):(ind_Z)]))
                    z = "{:.2f}".format(float(message[(ind_Z + 1):]))
                    print("X:", x, "Y:", y, "Z:", z)


class Uart:
    def __init__(self, port='/dev/serial0', boud=9600, timeout=1):
        self.uart = serial.Serial(port, boud, timeout=timeout)
        self.uart.flush()  # очистка юарта

    # Принять сообщение
    def accept_message(self):
        if self.uart.in_waiting > 0:
            line = self.uart.readline()
            print(line.decode("utf-8").rstrip())
            return line.decode("utf-8").rstrip()

    def send_message(self, message):
        self.uart.write(message)
        pass

    # распарсить сообщение
    def message_parse(self, message):
        ind_X = message.find("X")
        ind_Y = message.find("Y")
        ind_Z = message.find("Z")

        x = "{:.2f}".format(float(message[(ind_X + 1):(ind_Y)]))
        y = "{:.2f}".format(float(message[(ind_Y + 1):(ind_Z)]))
        z = "{:.2f}".format(float(message[(ind_Z + 1):]))
        print(x, y, z)
        return x, y, z


if __name__ == '__main__':
    client = Client(id="127.0.0.1", port=8000, ind_copter=1)
    client.run_server()
    pass
