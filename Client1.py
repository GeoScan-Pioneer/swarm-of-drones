import time
from SwarmUtils import Client
from time import sleep
from random import randint as rd

if __name__ == '__main__':
    client = Client(ip="127.0.0.1", port=8000, port_uart="COM1")
    client.run_UDP()
    client.send_message(message=client.create_message_SC(), destination=('localhost', 8000))
    print("Sent1")
    time.sleep(3)
    client.send_message(message=client.create_message_CC(rd(20, 580), rd(20, 580), 0), destination=('localhost', 8000))
    print("Sent2")
