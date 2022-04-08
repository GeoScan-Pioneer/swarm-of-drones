from swarm_sdk import Server

swarm = Server.Swarm()

swarm.add_copter('192.168.0.100', name='lead')
swarm.add_copter('192.168.0.101', name='back1')
swarm.add_copter('192.168.0.102', name='back2')

while True:
    if swarm.step_get() == 0:
        swarm.get_copter('lead').go_to_local_point(x=1, y=0, z=1.5)
        swarm.get_copter('back1').go_to_local_point(x=0, y=1, z=1.5)
        swarm.get_copter('back2').go_to_local_point(x=0, y=-1, z=1.5)
        swarm.wait_for_task_completion(ands=['lead', 'back1', 'back2'])
    if swarm.step_get() == 1:
        print('Hehe')
