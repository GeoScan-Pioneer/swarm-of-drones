import time

from SwarmUtils import Client
from time import sleep

if __name__ == '__main__':
    client = Client(ip="127.0.0.1", port=8000, port_uart="COM1")
    client.run_UDP()
    client.send_message(message=client.create_message_SC(), destination=('localhost', 8000))
    print("Sent")
