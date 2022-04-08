class Item:
    def __init__(self, name, action):
        self.__name = name
        self.__action = action

    def getAction(self):
        return self.__action

    def getName(self):
        return self.__name
    