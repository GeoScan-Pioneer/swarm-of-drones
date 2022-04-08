from swarm_sdk.Client import Copter
from typing import Dict
from threading import Thread


class Swarm:
    """ Сервер """

    def __init__(self):
        self.__copter_list = Dict[str: Copter]
        self.__copter_id_to_ip_map_table = Dict[str: str]
        self.__copter_ip_to_id_map_table = Dict[str: str]

        self.__wait_for_task_completion_thread = Thread(target=self.wait_for_task_completion)

        self.__step = 0
        self.__wait_called_on_step = None

    def step_get(self) -> int:
        """
        Возвращает текущий шаг программы.
        :return: int - шаг программы.
        """
        return self.__step

    def step_add(self, stp=1):
        """
        Увеличивает текущий шаг программы на 1.
        :param stp: шаг, на который изменится шаг :).
        :return: функция ничего не возвращает.
        """
        self.__step += stp

    def add_copter(self, ip, name=None):
        """
        Добавляет новый экземпляр квадрокоптера в рой.
        :param ip: ip адрес квадрокоптера в сети, передается как строка.
        :param name: уникальное имя квадрокоптера.
        :return: функция ничего не возвращает.
        """
        self.__copter_list.update({ip: Copter(ip)})
        if name is None:
            name = len(self.__copter_list)
        self.__copter_id_to_ip_map_table.update({name: ip})
        self.__copter_ip_to_id_map_table.update({ip: name})
        print(f'Copter with ip: {ip} has been successfully added! It`s own id(name): {name}')

    def get_copter(self, name=None, ip=None) -> Copter:
        """
        Возвращает экземпляр квадрокоптера из роя по id или ip.
        :param name: уникальное имя квадрокоптера.
        :param ip: ip адрес квадрокоптера.
        :return: Copter - объект квадрокоптера (класс-обертка над pioneer_sdk).
        """
        if ip is not None:
            return self.__copter_list.get(ip)
        if name is not None:
            return self.__copter_list.get( self.__copter_id_to_ip_map_table.get(name) )

    def move_abs(self, x=None, y=None, z=None, yaw=None):
        """
        Движение центра роя в абсолютные координаты.

        !!!!!!!В теукщем виде работать не будет!!!!!!
        !!!!!Все коптеры столнутся в одной точке!!!!

        :param x: координата x.
        :param y: координата y.
        :param z: коордната z.
        :param yaw: рысканье (радиан).
        :return: функция ничего не возвращает.
        """
        for copter in self.__copter_list.values():
            copter.go_to_local_point(x, y, z, yaw)

    def wait_for_task_completion(self, ands=[], ors=[], together=True, blocking=False):
        """
        Ожидание завершения выполнения задания роем
        :param ands: id коптеров, все из которых должны закончить выполнение задания. Если указать -1, то все.
        :param ors: id коптеров, из которых хотя бы один должен закончить задание. Если уакзать -1, то все.
        :param together: должны ли оба предыдущих списка быть True.
        :param blocking: пока ничего не делает.
        :return: True|False - закончили ли коптеры выполнять задание.
        """
        if self.__step is not None:
            self.__wait_called_on_step = self.__step
            self.__step = None
            self.__wait_for_task_completion_thread.run()
            return False

        while self.__step is None:
            ands_state = False
            ors_state = False

            if type(ands) == -1:
                ands = self.__copter_id_to_ip_map_table.keys()
            for i in ands:
                ip = self.__copter_id_to_ip_map_table.get(i)
                ands_state &= self.__copter_list.get(ip).get_task_completion_state()
            if len(ands) == 0:
                ands_state = True

            if type(ors) == -1:
                ors = self.__copter_id_to_ip_map_table.keys()
            for i in ors:
                ip = self.__copter_id_to_ip_map_table[i]
                ors_state |= self.__copter_list.get(ip).get_task_completion_state()
            if len(ors) == 0:
                ors_state = True

            if together:
                if ands_state and ors_state:
                    self.__step = self.__wait_called_on_step + 1
                    return True
            else:
                if ands_state or ors_state:
                    self.__step = self.__wait_called_on_step + 1
                    return True
