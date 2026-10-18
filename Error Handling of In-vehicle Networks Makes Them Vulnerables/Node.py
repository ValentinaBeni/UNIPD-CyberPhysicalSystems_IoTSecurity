from enum import Enum
import threading
import time
from Message import Message
from Bus import Bus


class NodeState(Enum):
    ERROR_ACTIVE = 0
    ERROR_PASSIVE = 1
    BUS_OFF = 2


class Node:
    """  
    Represents an ECU node in the CAN bus simulation. 
    Each node can be a normal ECU or an adversary ECU that manipulates its error state to disrupt communication. 
    The node  maintains its own Transmit Error Counter (TEC) and updates it based on the success or failure of message transmissions. 
    It also checks for duplicate message IDs on the bus and adjusts its error state accordingly. 
    The node runs a process that simulates sending messages, checking for duplicates, 
    and updating its TEC in a loop until the simulation is stopped or the node goes bus-off
    """
    def __init__(self, node_id: int, is_adversary: bool=False, adv_target_id: int=-1):
        self.is_adversary = is_adversary
        self.adv_target_id = adv_target_id
        self.node_id = node_id
        self.tec = 0
        self.error_flag = True
        self.retransmission = False
        self.retransmission_delay = 0.2
        self.status = NodeState.ERROR_ACTIVE
        self.tec_history = []
        self.sent_messages = {}


    def update_state(self) -> None:
        if self.tec <= 127:
            self.status = NodeState.ERROR_ACTIVE
        elif self.tec <= 254:
            self.status = NodeState.ERROR_PASSIVE
            self.retransmission_delay = 0.5
        else:
            self.status = NodeState.BUS_OFF


    def message_transmit_success(self) -> None:
        if self.status == NodeState.BUS_OFF:
            return
        if self.tec > 0:
            self.tec -= 1
            self.tec_history.append({'time': time.time(), 'tec': self.tec})
        self.update_state()


    def message_transmit_error(self) -> None:
        if self.status == NodeState.BUS_OFF:
            return
        self.tec += 8
        self.tec_history.append({'time': time.time(), 'tec': self.tec})
        self.update_state()


    def send_message(self, message: Message, canbus: Bus, retransmission=False) -> None:
        if not retransmission:
            self.sent_messages[message.id] = (message.data, message)

        with canbus.lock:
            canbus.message_log.append(message)
            if retransmission:
                print(f"ECU {self.node_id} is retransmitting message ID={message.id} with data={message.data} -> TEC = {self.tec}")
            else:
                print(f"ECU {self.node_id} sent message: ID={message.id} with data={message.data} -> TEC = {self.tec}")


    def check_duplicate_ids(self, message_id: int, canbus: Bus) -> None:
        with canbus.lock:
            duplicates = [msg for msg in canbus.message_log if msg.get_id() == message_id and msg.get_ecu_id() != self.node_id]
            if len(duplicates) > 0:                
                for duplicate in duplicates:
                    original_data, original_message = self.sent_messages[message_id]
                    if duplicate.to_array() != original_message.to_array():
                        self.retransmission = True
            else:   
                self.retransmission = False
    

    def update_tec(self, message_id: int, canbus: Bus) -> None:
        with canbus.lock:
            duplicates = [msg for msg in canbus.message_log if msg.get_id() == message_id and msg.get_ecu_id() != self.node_id]
            if len(duplicates) > 0:
                for duplicate in duplicates:
                    if self.is_adversary:
                        if self.status == NodeState.ERROR_ACTIVE and self.error_flag:
                            self.message_transmit_error()
                        elif self.status == NodeState.ERROR_PASSIVE or (self.status == NodeState.ERROR_ACTIVE and not self.error_flag):
                            self.message_transmit_success()
                            self.error_flag = False
                    else:
                        original_data, original_message = self.sent_messages[message_id]
                        if duplicate.to_array() != original_message.to_array():
                            if self.status == NodeState.ERROR_ACTIVE and self.error_flag:
                                self.message_transmit_error()  
                            elif self.status == NodeState.ERROR_PASSIVE and self.error_flag:
                                self.message_transmit_error()  
                                self.message_transmit_success()
                                self.error_flag = False
                            elif self.status == NodeState.ERROR_PASSIVE and not self.error_flag:
                                self.message_transmit_error()  
                                self.message_transmit_success() 
                                self.error_flag = False
            self.update_state()


    def run_process(self, message_id: int, data: list, canbus: Bus, barrier: threading.Barrier, simulation_state=None) -> None:
        while simulation_state == 'running' and canbus.is_ecu_connected(self.node_id) and len(canbus.connected_ecus) > 1:
            canbus.message_log.clear()
            self.update_state()

            if self.status == NodeState.BUS_OFF:
                with canbus.lock:
                    canbus.disconnect_ecu(self.node_id)
                simulation_state = 'stopped'
                break

            try:
                barrier.wait(timeout=1)
            except threading.BrokenBarrierError:
                barrier.reset()
                continue
            
            if self.retransmission:
                message = Message(self.node_id, message_id, self.sent_messages[message_id][0])
                self.send_message(message, canbus, retransmission=True)
            else:
                message = Message(self.node_id, message_id, data)
                self.send_message(message, canbus)

            try:
                barrier.wait(timeout=1)   
            except threading.BrokenBarrierError:
                barrier.reset()
                continue 

            self.check_duplicate_ids(message_id, canbus)

            try:
                barrier.wait(timeout=1)   
            except threading.BrokenBarrierError:
                barrier.reset()
                continue

            self.update_tec(message_id, canbus)
            
            time.sleep(self.retransmission_delay)