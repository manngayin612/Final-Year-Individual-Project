from telnetlib import STATUS
import VoiceRecognitionUtils as vr


class Item:

    def __init__(self, name, item_def, actions=[], action_def=[],success=False, description="blablabla"):
        self.__name = name
        self.__item_def = item_def
        self.__actions = {"investigate":"investigate.v.02"}
        for i in range(len(actions)):
            self.__actions[actions[i]] = action_def[i]
        self.success = success
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
                msg += vr.generateResponse("You have got {} in your bag.".format(self.getName()))

            elif input.action == "investigate":
                msg+= self.getDescription()
            else:
                msg+= vr.generateResponse("What do you want to do?")

        return msg

    def isRoomObject(self, room, input):
        return input in room.currentItems

    def isBagObject(self, room, input):
        return input in room.bag



# Items that need certain items to unlock
class UnlockItem(Item):
    def __init__(self, name,  unlock_msg, item_def,required_items="", actions=["unlock"], action_def=["unlock.v.03"],success = False, description="Exit Item"):
        super().__init__(name, item_def, actions, action_def, success, description=description)
        self.required_items = required_items
        self.unlock_message = unlock_msg

    def checkRequired(self, bag):
        return self.required_items in bag

    def performAction(self, room, input):
        msg = ""
        if input.action == "investigate":
            msg += self.getDescription()

        elif input.action == "unlock":
            if self.checkRequired(room.bag):
                msg += vr.generateResponse(self.unlock_message)
            else: 
                msg += vr.generateResponse("You might missed something like a {}".format(self.required_items))
        else:
            msg += vr.generateResponse("What do you want to do?")
        
        return msg

# Items that need password to unlock
class NumberLock(Item):
    def __init__ (self, name, password, item_def, actions=["unlock"], action_def=["unlock.v.01"],success=False, description="blablabla"):
        super().__init__(name, item_def, actions, action_def,success, description=description)
        self.password = password
    
    def unlockNumberLock(self, input):
        if input == self.password:
            self.success = True
            return True
        else:
            return False

    def performAction(self, room, input):
        msg = ""
        if input.action == "investigate":
            msg += self.getDescription()
        elif input.action == "unlock":
            if input.password == "":
                msg+= vr.generateResponse("Do you know the password for the {}?".format(self.getName()))
            else:  
                if self.unlockNumberLock(input.password):
                    msg += vr.generateResponse("Your had the correct password for the {}".format(self.getName()))
                else: 
                    msg += vr.generateResponse("I don't think it is correct.")
        else:
            msg += vr.generateResponse("What do you want to do?")
        
        return msg

class CombinableItem(Item):
    def __init__(self, name, item_def, combine_with, finished_item, actions=["get", "combine"], action_def=["get.v.01", "combine.v.04"], success=False, description=""):
        super().__init__(name, item_def, actions, action_def, success, description)
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
            print("Bag: {}, CurrentItems: {}")
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
            msg += vr.generateResponse("You have got {} in your bag.".format(self.getName()))
        elif input.action == "combine":
            if input.tool == "" :
                msg+= vr.generateResponse("What do you want to combine with {}".format(self.getName()))
            else:
                if self.isBagObject(room, input.tool) or self.isBagObject(room, self.getName()):
                    msg+=self.combineWith(room, input.tool)
                else:
                    msg+=vr.generateResponse("You have some missing pieces.")
        else:
            msg += vr.generateResponse("What do you want to do?")
        return msg

        

