from telnetlib import STATUS


class Item:

    def __init__(self, name, actions=["investigate"], status=[], description="blablabla", definition=["investigate.v.02"]):
        self.__name = name
        self.__actions = {"investigate":"investigate.v.02"}
        for i in range(len(actions)):
            self.__actions[actions[i]] = definition[i]
        self.__status = status
        self.__currentStatus = "" if status == [] else status[0]
        self.__description = description
        self.__def = definition
        

    def getActions(self):
        return self.__actions.items()

    def getName(self):
        return self.__name

    def getCurrentStatus(self):
        return self.__currentStatus

    def setCurrentStatus(self, status):
        if (status in self.__status):
            self.__currentStatus = status
    
    def getDescription(self, action):
        return self.__actions[action]
    


    

    # def setSpecialTool(self, action, tool):
    #     self.__actions[action] = tool

