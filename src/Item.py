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
        self.__def = action_def
        
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
    


    

    # def setSpecialTool(self, action, tool):
    #     self.__actions[action] = tool

