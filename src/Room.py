from Item import Item, NumberLock, UnlockItem
from SolvingPath import SolvingPath

class Room:

    def __init__(self, level, bag):
        self.level = level
        self.bag = bag
        self.items_in_room = []
        self.currentItems = ["key","door","table"]
        self.bag = []
        self.success = False


    def initialiseRoom(self):
        pass

class FirstRoom(Room):

    def __init__(self, level, bag):
        super().__init__(level, bag)

    def initialiseRoom(self):
        self.bag = []
        self.currentItems = ["key","door","table"]
        door = UnlockItem("door", item_def="door.n.01",actions=["unlock"], status=["locked", "unlocked"], action_def=["unlock.v.01"], required_items= "key",description="The door is locked now.", unlock_msg="You successfully escaped!")
        key = Item("key", item_def="key.n.01",action_def=["get.v.01"], actions=["get"])
        box = UnlockItem("box", item_def="box.n.01", actions=["open"], action_def=["open.v.01"], status=["opened", "closed"], description="You can't open the box. There is a lock on it.", unlock_msg="There is a key inside.")
        table = Item("table", item_def="table.n.02", description="There is a box on the table.")
        padlock = NumberLock("padlock", password="1234",item_def="padlock.n.01", description="It is a four digit lock." )
        self.items_in_room= [key, door, box, table, padlock]
        print("First Room Created!")
        return self.createSolutionPath()

    # Check if the door is unlocked 
    def doorUnlocked(self):
        self.success = self.getItem("door").getCurrentStatus() == "unlocked" 
        return self.success

    # Check if have item in bag
    def obtainedItem(self,item):
        return item in self.bag

    # Return the Item object with the name
    def getItem(self,item_name):
        for obj in self.items_in_room:
            if item_name == obj.getName():
                return obj
        return None


    def createSolutionPath(self):
        unlockDoor = SolvingPath(self.doorUnlocked, is_leaf=True)
        obtainedKey = SolvingPath(self.obtainedItem, cond_arg="key", next_steps=[unlockDoor])
        start = SolvingPath("start", next_steps=[obtainedKey])
        
        return start