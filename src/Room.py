from sqlalchemy import desc
from Item import CombinableItem, Item, NumberLock, UnlockItem
from SolvingPath import SolvingPath

class Room:

    def __init__(self, name, level, bag):
        self.name = name
        self.level = level
        self.bag = bag
        self.title = ""
        self.description = ""
        self.items_in_room = []
        self.currentItems = []
        self.bag = []
        self.success = False
        self.succeed_item = ""
        # self.starting_items = []

    # Check if have item in bag
    def obtainedItem(self,item):
        return item in self.bag

    # Return the Item object with the name
    def getItem(self,item_name):
        for obj in self.items_in_room:
            if item_name == obj.getName():
                return obj
        return None

    def addItem(self, item):
        if item not in self.items_in_room:
            self.items_in_room.append(item)
        
        if item.getName() not in self.currentItems:
            self.currentItems.append(item.getName())

    def initialiseRoom(self, list_of_items):

        self.bag = []
        room_details = list_of_items.pop(0)
        self.succeed_item = room_details[6]
        self.description = room_details[4]
        for row in list_of_items:
            # create the items first
            (type, item, item_def, actions, description, unlock_msg ,required_items ,unlock_action ,combine_with ,finished_item ) = row
            print("Initialising room:, ", actions)
            if type == "normal":
                item = Item(item, item_def, actions, description)
            elif type =="unlock":
                item = UnlockItem(item, item_def, unlock_msg=unlock_msg, required_items=required_items, actions=actions, unlock_action=unlock_action, description=description)
            elif type =="numberlock":
                item = NumberLock(item, required_items, item_def, actions=actions, description=description, unlock_msg=unlock_msg)
            elif type == "combine":
                item = CombinableItem(item, item_def, combine_with=combine_with, finished_item=finished_item, actions=actions, description=description)

            self.addItem(item)
        print(self.currentItems)
        print(self.items_in_room)

    def succeedCondition(self):
        self.success = self.getItem(self.succeed_item).success
        print(self.success)
        return self.success        


class FirstRoom(Room):

    def __init__(self, level, bag):
        super().__init__(level, bag)
        self.title = "Welcome to the first room."
        self.description = "You are in an empty room with a little wooden table in the middle of the room. Try to escape."



    def initialiseRoom(self):
        self.bag = []
        self.currentItems = ["key","door","table", "box"]
        door = UnlockItem("door", item_def="door.n.01", required_items= "key",description="The door is locked now.", unlock_msg="You successfully escaped!")
        key = Item("key", item_def="key.n.01", actions=["get"])
        box = NumberLock("box", item_def="box.n.01", description="You can't open the box. There is a lock on it.", unlock_msg="There is a key inside.", password = "1234")
        table = Item("table", item_def="table.n.02",  description="There is a box on the table.")
        # padlock = NumberLock("padlock", password="1234",item_def="padlock.n.01", description="It is a four digit lock." )
        self.items_in_room= [key, door, box, table]
        print("First Room Created!")


    # Check if the door is unlocked 
    def succeedCondition(self):
        self.success = self.getItem("door").success
        return self.success


    def createSolutionPath(self):
        unlockDoor = SolvingPath(self.doorUnlocked, is_leaf=True)
        obtainedKey = SolvingPath(self.obtainedItem, cond_arg="key", next_steps=[unlockDoor])
        start = SolvingPath("start", next_steps=[obtainedKey])
        
        return start


class SecondRoom(Room):

    def __init__(self, level, bag):
        super().__init__(level, bag)
        self.title = "Welcome to the second room."
        self.description = "There is nothing in the room but only a window and some pieces on the floor."

    def initialiseRoom(self):

        self.bag = []
        self.currentItems = ["ax_head", "handle", "window"]
        ax = Item("ax", item_def="ax.n.01", actions=["chop"], description="The axe is so heavy and sharp.") 
        ax_head = CombinableItem("ax_head", "ax_head.n.01", "handle", ax, description="This is the head of the axe.")
        handle = CombinableItem("handle", "handle.n.01", "ax_head", ax, description="This is the handle of the axe.")
        window = UnlockItem("window", item_def="window.n.01", actions=["break"], unlock_action="break", required_items= "ax",description="The window is made of glass.", unlock_msg="You successfully escaped!")
        self.items_in_room=[ax_head, handle, window]
        print("Second Room Created!")


    # Check if the door is unlocked 
    def succeedCondition(self):
        self.success = self.getItem("window").success
        return self.success
    
