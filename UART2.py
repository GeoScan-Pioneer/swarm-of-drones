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

            type_message = self.message_parser2(line)
            # команда ARM
            if type_message == 'CA':
                """выполнить предстартовую подготовку"""
                print("Получено сообщение CA")

            elif type_message == 'CD':
                """выполнить предстартовую подготовку"""
                print("Получено сообщение CD")

            elif type_message == "CL":
                """выполнить посадку"""
                print("Получено сообщение CL")

            elif type_message == "MR":
                """выполнить сброс груза"""
                print("Получено сообщение MR")

            # Если пришли новые координаты для коптера
            elif type_message == 'NC':
                __, __, X, Y, Z, __ = struct.unpack(">2cfff1c", line)
                print("Получено сообщение NC", X, Y, Z)

            elif type_message == 'SL':
                __, __, R, G, B, __ = struct.unpack(">2cfff1c", line)
                print("Получено сообщение SL", R, G, B)


    def send_message(self, message):
        self.uart.write(message)
        pass

    def create_message_CC(self, X, Y, Z):
        message = str("CC" "X" + str(X) + "Y" + str(Y) + "Z" + str(Z))+"\n"
        return message.encode("utf8")

    # распарсить сообщение
    def message_parser2(self, message):
        type_message = message[0:2].decode("utf-8")
        return type_message

uart = Uart(port="COM2")
while True:
    uart.accept_message()
