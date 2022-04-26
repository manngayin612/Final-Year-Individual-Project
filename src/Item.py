from telnetlib import STATUS


class Item:

    def __init__(self, name, item_def, actions=["investigate"], action_def=["investigate.v.02"],status=[], description="blablabla"):
        self.__name = name
        self.__item_def = item_def
        self.__actions = {"investigate":"investigate.v.02"}
        for i in range(len(actions)):
            self.__actions[actions[i]] = action_def[i]
        self.__status = status
        self.__currentStatus = "" if status == [] else status[0]
        self.__description = description
        
    def getItemDef(self):
        return self.__item_def


    def getActions(self):
        return self.__actions.items()

    def getName(self):
        return self.__name

    def getCurrentStatus(self):
        return self.__currentStatus

    def setCurrentStatus(self, status):
        if (status in self.__status):
            self.__currentStatus = status
    
    def getDescription(self):
        return self.__description



# Items that need certain items to unlock
class UnlockItem(Item):
    def __init__(self, name, required_items, item_def, actions=["investigate", "unlock"], action_def=["investigate.v.02", "unlocked.n.01"],status=["locked", "unlocked"], description="Exit Item"):
        super().__init__(name, item_def, actions=actions, action_def=action_def, status=status, description=description)
        self.required_items = required_items

    def checkRequired(self, bag):
        return self.required_items.getName() in self.bag

# Items that need password to unlock
class NumberLock(Item):
    def __init__ (self, name, password, item_def, actions=["investigate", "unlock"], action_def=["investigate.v.02", "unlocked.n.01"],status=["locked", "unlocked"], description="blablabla"):
        super().__init__(name, item_def, actions=["unlock"], action_def=["unlock.n.01"],status=["unlocked","locked"], description=description)
        self.password = password
    
    def checkPassword(self, input):
        return input == self.password
