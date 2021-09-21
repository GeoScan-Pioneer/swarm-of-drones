import socket
import threading
import time
import cv2
import numpy as np
import struct
import serial
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
        self.task_id = 0
        self.__task_complete_state = None

    def task_complete_state(self):
        return self.__task_complete_state

    def task_complete_state_reset(self):
        self.__task_complete_state = None

    def task_complete_state_set(self):
        self.__task_complete_state = True


class NetUtils:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

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
    def create_message_Magnet_Reset(self):
        return struct.pack(">2s1c", b'MR', b"\n")

    # COPTER_LAND
    def create_message_COPTER_LAND(self):
        return struct.pack(">2s1c", b'CL', b"\n")

    # COPTER_ARM
    def create_message_COPTER_ARM(self):
        return struct.pack(">2s1c", b'CA', b"\n")

    # COPTER_DISARM
    def create_message_COPTER_DISARM(self):
        return struct.pack(">2s1c", b'CD', b"\n")

    # New Coordinates + X + Y + Z
    def create_message_New_Coordinates(self, X, Y, Z):
        return struct.pack(">2sfff1c", b'NC', X, Y, Z, b"\n")

    # Set Leds
    def create_message_Set_Leds(self, R, G, B):
        return struct.pack(">2sfff1c", b'SL', R, G, B, b"\n")

    # Search in area. Предаются координаты двух точек прямоугольника
    def create_message_SA(self, X1, Y1, X2, Y2):
        return struct.pack(">2sffff1c", b'SA', X1, Y1, X2, Y2, b"\n")

    # Search in pont. Предаются координаты точки
    def create_message_SP(self, X, Y, Z):
        return struct.pack(">2sfff1c", b'SP', X, Y, Z, b"\n")

    # Start Communication
    def create_message_Start_Communication(self):
        return struct.pack(">2s1c", b'SC', b"\n")

    # координаты коптера для отправки на сервер
    def create_message_Copter_Coordinates(self, X, Y, Z):
        return struct.pack(">2sfff1c", b'CC', X, Y, Z, b"\n")

    def create_message_Task_Completed(self, task_id=-1):
        return struct.pack(">2si1c", b'TC', task_id, b"\n")

    # разбираем пришедшее сообщение
    def message_parser(self, message):
        type_message = message[0:2].decode("utf-8")
        return type_message

