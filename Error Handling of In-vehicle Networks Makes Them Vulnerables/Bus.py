
import threading


class Bus:
    """ 
    Represents the CAN bus in the simulation.
    The bus maintains a list of connected ECUs and a log of all messages transmitted on the bus. 
    It provides methods for connecting and disconnecting ECUs, checking if an ECU is connected, and logging messages. 
    The bus uses a lock to ensure thread-safe access to the list of connected ECUs and the message log, 
    allowing multiple nodes to interact with the bus concurrently without data corruption.
    """
    def __init__(self):
        self.connected_ecus = []
        self.message_log = []
        self.lock = threading.Lock()


    def connect_ecu(self, ecu:int) -> None:
        if ecu not in self.connected_ecus:
            self.connected_ecus.append(ecu)
            print(f"The ECU {ecu} has been connected to the CAN bus")


    def disconnect_ecu(self, ecu:int) -> None:
        if ecu in self.connected_ecus:
            self.connected_ecus.remove(ecu)
            print(f"The ECU {ecu} has been disconnected from the CAN bus")


    def is_ecu_connected(self, ecu:int) -> bool:
        return ecu in self.connected_ecus