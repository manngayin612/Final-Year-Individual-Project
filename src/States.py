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
    EXTRA_ITEM = 12

states_dict = {}
states_dict[States.NAME_ROOM] = "It's time to create your own room! Lock the people up and watch them suffer...Before that...How should we call your room?" 
states_dict[States.OVERALL_DESCRIPTION] = "Imagine all those silly faces in the dark, they have no idea what's in here, tell them what you see."
states_dict[States.UPDATE_STORED_ITEM] = "update stored item"
states_dict[States.ASK_FOR_UNLOCK_ITEM] = "Do you unlock it with a password?"
states_dict[States.FILL_IN_UNLOCK_ITEM] = "Okay, no password. How do you unlock it then. I assume not by force?"
states_dict[States.FILL_IN_PASSWORD] = "Great, password is the easy way, but sorry we just do numeric here. Just tell me the number is fine."
states_dict[States.CONGRATS_MSG] = "What do you want to say to them after unlocking this item? Perhaps congratulating them for escaping from this hell... or maybe give them some tips?"
states_dict[States.ADD_MORE] = "Do you have more to add. I hope you don't make it too easy for them..."
states_dict[States.FINISHED] = "The room is now ready! I can't wait to see them struggling in here."
states_dict[States.EXTRA_ITEM] = "What else do you want to add?"