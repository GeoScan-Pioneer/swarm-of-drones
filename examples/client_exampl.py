from swarm_sdk.SwarmUtils import Client

import time
import random

if __name__ == '__main__':
    client = Client(ip="127.0.0.1", port=8001, port_uart="COM1")
    client.run_UDP()
    client.send_message(message=client.create_message_SC(), destination=('localhost', 8000))



    print("Sent1")
    time.sleep(3)

    x = 50
    y = 50
    while True:
        print(x, y)
        client.send_message(message=client.create_message_CC(x, y, 0), destination=('localhost', 8000))
        x = x + 0.1 * random.uniform(-1, 1)
        y = y + 0.1 * random.uniform(-1, 1)
        time.sleep(0.25)



    print("Sent2")
