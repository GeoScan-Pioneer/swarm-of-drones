import time

import serial
import struct

geit = ">2sf1sf1sf1c"

class Uart:
    def __init__(self, port='/dev/serial0', boud=9600, timeout=1):
        print(port)
        self.uart = serial.Serial(port, boud, timeout=timeout)
        self.uart.flush()  # очистка юарта

    # Принять сообщение
    def accept_message(self):
        if self.uart.in_waiting > 0:
            line = self.uart.readline()
            print(line.decode("utf-8").rstrip())

    def send_message(self, message):
        self.uart.write(message)
        pass

    def create_message_CC(self, X, Y, Z):
        #message = b"CC" + str(X) + b"Y" + str(Y) + b"Z" + str(Z)+"\n"

        start_message = b'CC'
        message_x = X
        start_message_Y = b"Y"
        message_y = Y
        start_message_Z = b"Z"
        message_z = Z
        message_finish = b"\n"
        #print(struct.pack(">2sfff1c", start_message,message_x,message_y,message_z,message_finish))
        #print(len(struct.pack(">2sfff1c", start_message,message_x,message_y,message_z,message_finish)))
        return struct.pack(">2sfff1c", start_message,message_x,message_y,message_z,message_finish)

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

uart = Uart(port="COM2")
#uart = Uart()
r = 0
b = 0
g = 0
n = 1
h = 0
while True:
    uart.send_message(uart.create_message_CC(r, g, b))
    r += 0.1*n
    b += 0.1*n
    g += 0.1*n

    h += 1
    if(h >= 9):
        n = n * -1
        h = 0
    time.sleep(1)
