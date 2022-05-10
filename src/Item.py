from os import unlink
from telnetlib import STATUS
import VoiceRecognitionUtils as vr


class Item:

    def __init__(self, name, item_def, actions=[], action_def=[], description="blablabla"):
        self.__name = name
        self.__item_def = item_def
        self.__actions = {"investigate":"investigate.v.02"}
        for i in range(len(actions)):
            self.__actions[actions[i]] = action_def[i]
        self.success = False
        self.__description = description
        
    def getItemDef(self):
        return self.__item_def


    def getActions(self):
        return self.__actions.items()

    def getName(self):
        return self.__name

    
    def getDescription(self):
        return self.__description

    def performAction(self, room,input):
        msg = ""
        if input.action!="":
            if input.action == "get":
                room.bag.append(self.getName())
                room.currentItems.remove(self.getName())
                msg += "You have got {} in your bag.".format(self.getName())

            elif input.action == "investigate":
                msg+= self.getDescription()
            else:
                msg+= "What do you want to do?"

        return vr.generateResponse(msg)

    def isRoomObject(self, room, input):
        return input in room.currentItems

    def isBagObject(self, room, input):
        return input in room.bag



# Items that need certain items to unlock
class UnlockItem(Item):
    def __init__(self, name,  unlock_msg, item_def, required_items="", actions=["unlock"], action_def=["unlock.v.03"], unlock_action = "unlock", description="Exit Item"):
        super().__init__(name, item_def, actions, action_def, description=description)
        self.required_items = required_items
        self.unlock_message = unlock_msg
        self.unlock_action = unlock_action

    def checkRequired(self, bag):
        return self.required_items in bag

    def performAction(self, room, input):
        msg = ""
        if input.action == "investigate":
            msg += self.getDescription()

        elif input.action == self.unlock_action:
            if self.checkRequired(room.bag):
                msg += self.unlock_message
                self.success = True
            else: 
                msg += "You might missed something like a {}".format(self.required_items)
        else:
            msg += "What do you want to do?"
        
        return vr.generateResponse(msg)

# Items that need password to unlock
class NumberLock(UnlockItem):
    def __init__ (self, name, password, item_def, actions=["unlock"], action_def=["unlock.v.03"], description="blablabla", unlock_msg="You have got the correct password"):
        super().__init__(name, unlock_msg, item_def, actions=actions, action_def = action_def, description=description,)
        self.password = password

    
    def unlockNumberLock(self, input):
        if input == self.password:
            self.success = True
        return self.success

    def performAction(self, room, input):
        msg = ""
        if input.action == "investigate":
            msg += self.getDescription()
        elif input.action == "unlock":
            if input.password == "":
                msg+= "Do you know the password for the {}?".format(self.getName())
            else:  
                if self.unlockNumberLock(input.password):
                    msg += self.unlock_message
                else: 
                    msg += "I don't think it is correct."
        else:
            msg += "What do you want to do?"
        
        return vr.generateResponse(msg)

class CombinableItem(Item):
    def __init__(self, name, item_def, combine_with, finished_item, actions=["get", "combine"], action_def=["get.v.01", "combine.v.04"], description=""):
        super().__init__(name, item_def, actions, action_def, description)
        self.finished_item = finished_item
        self.combine_with = combine_with


 


    def combineWith(self, room, component):
        if component.getName() == self.combine_with:
            room.bag.append(self.finished_item.getName())

            if self.getName() in room.bag: room.bag.remove(self.getName()) 
            else: room.currentItems.remove(self.getName())

            if component.getName() in room.bag: room.bag.remove(component.getName()) 
            else: room.currentItems.remove(component.getName())
            
            
            room.items_in_room.append(self.finished_item)
            room.items_in_room.remove(self)
            room.items_in_room.remove(component)
            print("Bag: {}, CurrentItems: {}".format(room.bag, room.currentItems))
            return vr.generateResponse("You have successfully combined {} and {}. You got a new {}".format(self.getName(), component, self.finished_item.getName()))
        else:
            return vr.generateResponse("You cannot combine {} with {}.".format(self.getName(), component))
            


    def performAction(self, room, input):
        print(input.tool)
        msg = ""
        if input.action == "investigate":
            msg += self.getDescription()
        elif input.action == "get":
            room.bag.append(self.getName())
            room.currentItems.remove(self.getName())
            msg += "You have got {} in your bag.".format(self.getName())
        elif input.action == "combine":
            if input.tool == "" :
                msg+="What do you want to combine with {}".format(self.getName())
            else:
                if self.isBagObject(room, input.tool) or self.isBagObject(room, self.getName()):
                    msg+=self.combineWith(room, input.tool)
                else:
                    msg+="You have some missing pieces."
        else:
            msg += "What do you want to do?"
        return vr.generateResponse(msg)

        

