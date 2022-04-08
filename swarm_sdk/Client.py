from pioneer_sdk.asynchronous import Pioneer
import time
import threading


class Copter(Pioneer):
    def __init__(self, ip, video_port=8888, mav_port=8001):
        super(Copter, self).__init__(pioneer_ip=ip,
                                     pioneer_video_control_port=video_port,
                                     pioneer_mavlink_port=mav_port)

        # Текущие состояние: Waiting, Moving, Armed, Landed
        self.condition = "Waiting"

        # массив хранения текущих координат коптера
        self.coordinates = [0, 0, 0]
        # координаты дома (берутся при взлете)
        self.home = [0, 0, 0]