from swarm_sdk.Server import Server
from swarm_sdk.SwarmUtils import Card

if __name__ == '__main__':
    card = Card()
    server = Server(ip_server='localhost', port_serer=8000, card=card)
    print(1)
    server.run_UDP()
