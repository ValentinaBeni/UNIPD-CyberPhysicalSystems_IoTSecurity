class Message:
    """
    Represents a CAN message in the simulation.
    Each message has an associated ECU ID (the sender), a message ID, and a data payload.
    The class provides methods to convert the message to an array format for logging and 
    to retrieve its components (ECU ID, message ID, and data).
    """
    def __init__(self, ecu_id: int, id: int, data: list):
        self.ecu_id = ecu_id
        self.id = id
        self.data = data


    def to_array(self) -> list: 
        return [self.ecu_id, self.id, self.data]


    def get_ecu_id(self) -> int:
        return self.ecu_id


    def get_id(self) -> int:
        return self.id


    def get_data(self) -> list:
        return self.data