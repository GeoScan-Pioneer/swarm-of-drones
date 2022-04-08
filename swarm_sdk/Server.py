from swarm_sdk.Client import Copter

class Server:
    """ Сервер """

    def __init__(self):
        self.__copter_list = {}
        self.__copter_id_to_ip_map_table = {}
        self.__copter_ip_to_id_map_table = {}

    def add_copter(self, ip, name=None):
        self.__copter_list.update({ip: Copter(ip)})
        if name is None:
            name = len(self.__copter_list)
        self.__copter_id_to_ip_map_table.update({name: ip})
        self.__copter_ip_to_id_map_table.update({ip: name})
        print(f'Copter with ip: {ip} has been successfully added! It`s own id(name): {name}')