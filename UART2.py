import serial
import struct

geit = ">2sfffc"

class Uart:
    def __init__(self, port='/dev/serial0', boud=9600, timeout=1):
        print(port)
        self.uart = serial.Serial(port, boud, timeout=timeout)
        self.uart.flush()  # очистка юарта

    # Принять сообщение
    def accept_message(self):
        if self.uart.in_waiting > 0:
            line = self.uart.readline()
            m1, m2, m3, m4, m5, m6 = struct.unpack(">2cfff1c", line)
            print(m1, m2, m3, m4, m5, m6)

    def send_message(self, message):
        self.uart.write(message)
        pass

    def create_message_CC(self, X, Y, Z):
        message = str("CC" "X" + str(X) + "Y" + str(Y) + "Z" + str(Z))+"\n"
        return message.encode("utf8")

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
while True:
    uart.accept_message()
