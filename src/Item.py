from telnetlib import STATUS


class Item:

    def __init__(self, name, actions=["investigate"], status=[], description="blablabla"):
        self.__name = name
        self.__actions = {"investigate":""}
        for a in actions:
            self.__actions[a] = ""
        self.__status = status
        self.__currentStatus = "" if status == [] else status[0]
        self.__description = description
        

    def getActions(self):
        return self.__actions

    def getName(self):
        return self.__name


    def getCurrentStatus(self):
        return self.__currentStatus

    def setCurrentStatus(self, status):
        if (status in self.__status):
            self.__currentStatus = status
    
    def getDescription(self):
        return self.__description

    def setSpecialTool(self, action, tool):
        self.__actions[action] = tool

