import socket
import threading
import time


class Server():
    def __init__(self, id, port):
        self.id_server = id
        self.port_server = port

        self.serv_sock = None
        self.clients_sock = []

        self.cid = 0
        self.clients_message = []

    # Запустить сервер
    def run_server(self):
        self.serv_sock = self.__create_serv_sock()  # создание сервера
        t1 = threading.Thread(target=self.message_handler, args=())  # запуск потока обработки сообщений
        t1.start()

        while True:
            client_sock, client_addr = self.serv_sock.accept()  # если есть подключение
            self.clients_sock.append(client_sock)  # сохраняем в список подключенных устройств
            print("Клиент", client_addr, "подключился")
            t = threading.Thread(target=self.accept_message_client,
                                 args=(client_sock, self.cid))  # запускаем поток его обработки
            t.start()
            self.cid += 1

    # Создать соккет
    def __create_serv_sock(self):
        serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
        serv_sock.bind((self.id_server, self.port_server))
        serv_sock.listen()
        return serv_sock

    # отлдельный поток для приема сообщений от нового клиента
    def accept_message_client(self, client_sock, cid):
        while True:
            request = client_sock.recv(1024)
            # print(request.decode("utf8"))
            self.clients_message.append(request.decode("utf8"))  # запись всех полученных сообщений в список

    #########################################
    # Блок отправления и создания сообщений #
    #########################################
    def send_message(self, cid, message):
        self.clients_sock[cid].sendall(message)

    def create_message_H(self):
        return "HS".encode("utf8")

    def create_message_NC(self, X, Y, Z):
        message = "NC" + "X" + str(X) + "Y" + str(Y) + "Z" + str(Z)
        return message.encode("utf8")

    # разбираем пришедшее сообщение
    def message_parser(self, message):
        num_copter = message[0]
        type_message = message[1:3]
        message = message[3:len(message)]
        return num_copter, type_message, message

    ###################################
    # Блок анализа принятых сообщений #
    ###################################
    def message_handler(self):
        while True:
            # Если есть принятое сообщение
            if len(self.clients_message) > 0:

                # считываем сообщение и удаляем его
                message = self.clients_message.pop(0)
                num_copter, type_message, message = self.message_parser(message)

                # Если пришли координаты
                if type_message == 'CC':
                    ind_X = message.find("X")
                    ind_Y = message.find("Y")
                    ind_Z = message.find("Z")
                    x = "{:.2f}".format(float(message[(ind_X + 1):(ind_Y)]))
                    y = "{:.2f}".format(float(message[(ind_Y + 1):(ind_Z)]))
                    z = "{:.2f}".format(float(message[(ind_Z + 1):]))
                    print("Коптер", num_copter, "X:", x, "Y:", y, "Z:", z)

                    self.send_message(0, self.create_message_NC(X=13.4, Y=213.43, Z=45.20))

                # Если пришел найденный маркер
                elif type_message == 'DM':
                    print("Обнаружен маркер:", message)


if __name__ == '__main__':
    server = Server(id="127.0.0.1", port=8000)
    server.run_server()
