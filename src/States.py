import enum
class States(enum.Enum):
    NAME_ROOM = 1
    OVERALL_DESCRIPTION = 2
    INPUT_PROCESS = 3
    UPDATE_STORED_ITEM = 4
    CREATE_NEW_ITEMS = 5
    FILL_IN_UNLOCK = 6


states_dict = {}
states_dict[States.NAME_ROOM] = "What do you want to call your room?"
states_dict[States.OVERALL_DESCRIPTION] = "Tell me about the room:"
states_dict[States.UPDATE_STORED_ITEM] = "update stored item"
states_dict[States.FILL_IN_UNLOCK] = "Do you unlock it with a password?"