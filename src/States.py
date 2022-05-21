import enum
class States(enum.Enum):
    NAME_ROOM = 1
    UPDATE_STORED_ITEM = 2

states_dict = {}
states_dict[States.NAME_ROOM] = "What do you want to call your room?"
states_dict[States.UPDATE_STORED_ITEM] = "Tell me about the room:"