import socket
import threading
import time
import cv2
import numpy as np
import struct
import serial

try:
    import tkinter as tk
except:
    print("No module named tkinter. Do you need it??")

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