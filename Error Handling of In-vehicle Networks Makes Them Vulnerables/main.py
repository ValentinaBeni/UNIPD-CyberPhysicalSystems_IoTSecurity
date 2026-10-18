from Node import Bus, Node
import threading
from utils import plot_tec_history

global simulation_state 

simulation_state = 'running' 

canbus = Bus()
victim = Node(1)
adversary = Node(2, is_adversary=True, adv_target_id=1)

canbus.connect_ecu(victim.node_id)
canbus.connect_ecu(adversary.node_id)

barrier = threading.Barrier(2)

thread1 = threading.Thread(target=victim.run_process, args=(1, [1, 1, 1], canbus, barrier, simulation_state))
thread2 = threading.Thread(target=adversary.run_process, args=(1, [1, 1, 0], canbus, barrier, simulation_state))

thread1.start()
thread2.start()

thread1.join()
thread2.join()

plot_tec_history(victim, adversary)