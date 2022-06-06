import enum
class States(enum.Enum):
    NAME_ROOM = 1
    OVERALL_DESCRIPTION = 2
    INPUT_PROCESS = 3
    UPDATE_STORED_ITEM = 4
    CREATE_NEW_ITEMS = 5
    ASK_FOR_UNLOCK_ITEM = 6
    FILL_IN_UNLOCK_ITEM = 7
    FILL_IN_PASSWORD = 8
    CONGRATS_MSG = 9
    ADD_MORE = 10
    FINISHED = 11

states_dict = {}
states_dict[States.NAME_ROOM] = "What do you want to call your room?"
states_dict[States.OVERALL_DESCRIPTION] = "Tell me about the room:"
states_dict[States.UPDATE_STORED_ITEM] = "update stored item"
states_dict[States.ASK_FOR_UNLOCK_ITEM] = "Do you unlock it with a password?"
states_dict[States.FILL_IN_UNLOCK_ITEM] = "How do you unlock this item"
states_dict[States.FILL_IN_PASSWORD] = "What is the password for the lock"
states_dict[States.CONGRATS_MSG] = "What do you want to say to them after unlocking the item?"
states_dict[States.ADD_MORE] = "Do you have anything else to add? "
states_dict[States.FINISHED] = "The room is ready!"