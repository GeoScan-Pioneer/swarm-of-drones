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
    def __init__(self, width_cm=300, height_cm=300):
        # размеры полетной зоны в сантиметрах
        self.widm = width_cm
        self.hegm = height_cm

        threading.Thread.__init__(self)
        self.start()

    def callback(self):
        self.window.quit()

    def run(self):
        # pixels per cm
        self.__ppc = 0.8

        # размеры карты в пикселях
        self.__widp = round(self.widm * self.__ppc)
        self.__hegp = round(self.hegm * self.__ppc)

        self.__pad = round(30 * self.__ppc)

        self.window = tk.Tk()
        self.window.title("Live map")
        self.window['bg'] = 'white'
        self.window.resizable(width=False, height=False)
        self.window.config(padx=0, pady=0)
        self.window.geometry(f'{self.__widp + self.__pad * 2}x{self.__hegp + self.__pad * 2}')

        self.canvas = tk.Canvas(self.window)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.__grid_step = round(50 * self.__ppc)

        for i in range(self.__widp // self.__grid_step + 1):
            self.canvas.create_line(i * self.__grid_step + self.__pad, self.__pad,
                                    i * self.__grid_step + self.__pad, self.__hegp + self.__pad, fill="#AAAAAA")

            self.canvas.create_text(i * self.__grid_step + self.__pad, self.__pad // 2,
                                    text=i * round(self.__grid_step / self.__ppc))

        for i in range(self.__hegp // self.__grid_step + 1):
            self.canvas.create_line(self.__pad, i * self.__grid_step + self.__pad,
                                    self.__widp + self.__pad, i * self.__grid_step + self.__pad, fill="#AAAAAA")

            self.canvas.create_text(self.__pad // 2, i * self.__grid_step + self.__pad,
                                    text=i * round(self.__grid_step / self.__ppc))

        self.canvas.create_text(self.__pad + self.__widp // 2, self.__pad + self.__hegp + self.__pad // 2,
                                text="CM x CM")

        # размеры коптеров В САНТИМЕТРАХ
        self.__copter_radius = 19
        self.__copter_danger_area_radius = 29

        self.window.mainloop()

    def add_copter(self):
        oval1 = self.canvas.create_oval(self.__widp / 2 - self.__copter_danger_area_radius // 2,
                                        self.__hegp / 2 - self.__copter_danger_area_radius // 2,
                                        self.__widp / 2 + self.__copter_danger_area_radius // 2,
                                        self.__hegp / 2 + self.__copter_danger_area_radius // 2,
                                        outline="#FFAAAA", fill="#FFDDDD")
        oval2 = self.canvas.create_oval(self.__widp / 2 - self.__copter_radius // 2,
                                        self.__hegp / 2 - self.__copter_radius // 2,
                                        self.__widp / 2 + self.__copter_radius // 2,
                                        self.__hegp / 2 + self.__copter_radius // 2,
                                        outline="#FF0000", fill="#FF0000")
        return oval1, oval2

    def cm_to_px(self, x, y, target_oval):
        if target_oval == 1:
            x = round(x * 100 * self.__ppc) + self.__copter_radius / 2
            y = round(y * 100 * self.__ppc) + self.__copter_radius / 2
        elif target_oval == 2:
            x = round(x * 100 * self.__ppc) + self.__copter_danger_area_radius / 2
            y = round(y * 100 * self.__ppc) + self.__copter_danger_area_radius / 2
        return x, y


class Copter:
    def __init__(self, num_copter, addr, visual):
        self.num_copter = num_copter
        self.coords = (0, 0, 0)
        self.addr = addr
        self.condition = None
        self.visual = visual
        self.__task_complete_state = None

    def task_complete_state(self):
        return self.__task_complete_state

    def task_complete_state_reset(self):
        self.__task_complete_state = None

    def task_complete_state_set(self, state):
        if type(state) is not bool:
            print("Error! You have been set not a boolean value to the completion state of a task of the copter!")
            print("Your value has been overwritten to 'False'")
            self.__task_complete_state = False
        else:
            self.__task_complete_state = state


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

    def create_message_Task_Completed(self):
        return struct.pack(">2s1c", b'TC', b"\n")

    def create_message_Task_Skip(self):
        return struct.pack(">2s1c", b'TS', b"\n")

    # разбираем пришедшее сообщение
    def message_parser(self, message):
        type_message = message[0:2].decode("utf-8")
        return type_message

