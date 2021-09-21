from swarm_sdk.Client import Client

import time
import random

if __name__ == '__main__':
    client = Client(ip="127.0.0.1", port=8001, port_uart="COM1")
    client.run_UDP()


    print("Sent1")
    time.sleep(3)

    x = random.randint(30, 300)
    y = random.randint(30, 300)
    while True:
        # print(x, y)
        #client.send_message(message=client.create_message_Copter_Coordinates(x, y, 1), destination=('localhost', 8000))
        x = x + 0.1 * random.uniform(-1, 1)
        y = y + 0.1 * random.uniform(-1, 1)
        time.sleep(0.25)
