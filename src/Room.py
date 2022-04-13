from Item import Item

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
        door = Item("door", item_def="door.n.01",actions=["unlock", "open"], status=["locked", "unlocked"], action_def=["unlock.v.01",'open.v.01'], description="There is a lock on the door.")
        key = Item("key", item_def="key.n.01",action_def=["get.v.01"], actions=["get"], description="The key may be used to unlock something.")
        table = Item("table", item_def="table.n.02", description="There is a key on the table.")
        self.items_in_room= [key, door, table]
        print("First Room Created!")

    # Check if the door is unlocked 
    def doorUnlocked(self):
        self.success = self.getItem("door").getCurrentStatus() == "unlocked" 
        return self.success

    # Return the Item object with the name
    def getItem(self,item_name):
        for obj in self.items_in_room:
            if item_name == obj.getName():
                return obj
        return None

