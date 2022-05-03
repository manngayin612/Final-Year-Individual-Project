from sqlalchemy import desc
from Item import CombinableItem, Item, NumberLock, UnlockItem
from SolvingPath import SolvingPath

class Room:

    def __init__(self, level, bag):
        self.level = level
        self.bag = bag
        self.title = ""
        self.description = ""
        self.items_in_room = []
        self.currentItems = []
        self.bag = []
        self.success = False
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

    def initialiseRoom(self):
        pass

    def succeedCondition(self):
        pass

class FirstRoom(Room):

    def __init__(self, level, bag):
        super().__init__(level, bag)
        self.title = "Welcome to the first room."
        self.description = "You are in an empty room with a little wooden table by the window. Try to escape."

    def initialiseRoom(self):
        self.bag = []
        self.currentItems = ["key","door","table", "box"]
        door = UnlockItem("door", item_def="door.n.01", required_items= "key",description="The door is locked now.", unlock_msg="You successfully escaped!")
        key = Item("key", item_def="key.n.01",action_def=["get.v.01"], actions=["get"])
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
        ax = Item("ax", item_def="ax.n.01", actions=["chop"], action_def=["chop.v.06"], description="The axe is so heavy and sharp.") 
        ax_head = CombinableItem("ax_head", "ax_head.n.01", "handle", ax, description="This is the head of the axe.")
        handle = CombinableItem("handle", "handle.n.01", "ax_head", ax, description="This is the head of the axe.")
        window = UnlockItem("window", item_def="window.n.01", actions=["break"], action_def=["break.v.01"], unlock_action="break", required_items= "axe",description="The window is made of glass.", unlock_msg="You successfully escaped!")
        self.items_in_room=[ax_head, handle, window]

        print("Second Room Created!")


    # Check if the door is unlocked 
    def succeedCondition(self):
        self.success = self.getItem("window").success
        return self.success
    
