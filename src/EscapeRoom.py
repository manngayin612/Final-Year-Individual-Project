from py import process
import VoiceRecognitionUtils as vr 
from Item import Item
import json

# import nltk
# nltk.download('wordnet', force=True)
# nltk.download('omw-1.4', force=True)
# from nltk.corpus import wordnet as wn

voice_input = False
test = False
success = False
objects=[]
current_room_items = ["key", "door", "table"]
bag = []

def initialiseRoom():
    f = open("room_details.json")
    data = json.load(f)
    f.close()

    door = Item("door", actions=["unlock", "open"], status=["locked", "unlocked"])
    door.setSpecialTool("unlock", "key")
    key = Item("key", actions=["pick_up"])
    table = Item("table")
    objects.extend([door, key, table])



# f = open('room_details.json')
# data = json.load(f)
# f.close()

# objects = [items['name'] for items in data["items_in_rooms"]]

# print("Room Created!")

def findItems(item):
    for obj in objects:
        if item == obj.getName():
            return obj
    return "No such item in the room"

def processAction(action, subject, direct_object, indirect_object):

    item = findItems(direct_object)



    for a in item.getActions():
        print(a)
        if action in vr.getSynsetsList(a):
            if a == "pick_up":
                bag.append(item.getName())
                current_room_items.remove(item.getName())
            elif a == "investigate":
                print(item.getDescription())
    
    if item.getName() == "door" and action in vr.getSynsetsList("unlock"):
        item.setCurrentStatus("unlocked")
        print(item.getName(), item.getCurrentStatus())
        
        
    print(current_room_items, bag)


        
    
        
    
    # if action == "pick up" or action in vr.getSynsetsList("pick_up"):

    #     if direct_object in objects:
    #         objects.remove(direct_object)
    #         bag.append(direct_object)

    #     else: 
    #         print("No such object")
    # else:
    #     print("what do you want me to do?")
    # print(objects)
    # print(bag)
        

if __name__ == "__main__":

    if not test:
        initialiseRoom()
        while not success:

  
            
            if voice_input:
                user_input = vr.recogniseSpeech()
                print("Google Speech Recognition thinks you said \"" + user_input + "\"")
            else :
                user_input = input("Waiting for input... ")
                print("Input is \"" + user_input + "\"")

            action, subject, direct_object, indirect_object = vr.processSpeech(user_input)

            processAction(action, subject, direct_object, indirect_object)

            success = objects[0].getCurrentStatus() =="unlocked"


        print("end of game")
    else:
        initialiseRoom()
        print(objects)
            

