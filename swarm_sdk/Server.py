from swarm_sdk.SwarmUtils import NetUtils, Copter, Card
from typing import List

import time
import threading
import struct

class Server(NetUtils):
    """ Сервер """
    def __init__(self, ip_server, port_serer, card, number=4):
        super().__init__(ip=ip_server, port=port_serer)

        self.clients: List[Copter] = [] # список клиентов
        self.cid = 0

        self.card = card

        # список сообщений от клиентов
        self.clients_message = []

        self.step = 0

    def next_step(self):
        if self.step // 1 == self.step:
            self.step += 1
        else:
            self.step += 0.5

    def next_micro_step(self):
        self.step += 0.5

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
            #client = self.get_client_by_id(-1)
            self.card.canvas.moveto(client.visual[0], *self.card.cm_to_px(X, Y, 1))
            self.card.canvas.moveto(client.visual[1], *self.card.cm_to_px(X, Y, 2))
            print(X, Y, Z)

        # Если задача завершена
        elif type_message == "TC":
            self.get_client_by_address(client_addr).task_complete_state_set()

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

    # передается минимально допустимое расстояние
    def check_min_distance(self, min_distance):
        ind_copters = []
        for i in range(len(self.clients)):
            for j in range(i + 1, len(self.clients)):
                dist = self.__dist(self.clients[i].coordinates_copter[0], self.clients[j].coordinates_copter[0])
                if dist <= min_distance:
                    ind_copters.append((i, j))
        return ind_copters

<<<<<<< HEAD
    def main(self):
        """ Проверка минимального расстояния """
        ind_copters = self.check_min_distance(min_distance=1.5)

        if len(ind_copters) != 0:
            pass
        """ Отправка корректировок по итогам проверки расстояний"""

        """ Проверка состояния каждого дрона"""

        """ Перераспределение ролей, если состояния не удовлетворяют желаемым"""

=======
>>>>>>> development-2
    #########################
    # Блок тестовых функций #
    #########################

    def test_message(self):
        while True:
            if len(self.clients) > 0:
                self.send_message(destination=self.clients[0].addr, message=self.create_message_COPTER_ARM())
                time.sleep(2)

                self.send_message(destination=self.clients[0].addr, message=self.create_message_COPTER_LAND())
                time.sleep(2)

                self.send_message(destination=self.clients[0].addr, message=self.create_message_COPTER_DISARM())
                time.sleep(2)

                self.send_message(destination=self.clients[0].addr, message=self.create_message_New_Coordinates(10.30, 49.33, 1.00))
                time.sleep(2)

                self.send_message(destination=self.clients[0].addr, message=self.create_message_Set_Leds(0.30, 0.33, 1.00))

                time.sleep(2)



