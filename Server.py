from SwarmUtils import Card, Server

if __name__ == '__main__':
    card = Card()
    server = Server(ip_server='localhost', port_serer=8000, card=card)
    server.run_UDP()
