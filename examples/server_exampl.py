import time

from swarm_sdk.Server import Server
from swarm_sdk.SwarmUtils import Card


if __name__ == '__main__':
    card = Card()
    server = Server(ip_server='localhost', port_serer=8000, card=card)
    server.run_UDP()

    while True:
        if len(server.clients) > 0:
            if server.step == 0:
                server.send_message(server.clients[0].addr, server.create_message_New_Coordinates(20, 20, 1))
                server.next_micro_step()
            if server.step == 0.5:
                if server.clients[0].task_complete_state():
                    server.clients[0].task_complete_state_reset()
                    server.next_micro_step()
            if server.step == 1:
                server.send_message(server.clients[0].addr, server.create_message_Set_Leds(255, 0, 0))
                server.next_step()
