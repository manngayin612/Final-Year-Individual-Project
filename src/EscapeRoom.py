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
objects=[]
current_room_items = ["key", "door", "table"]
bag = []

def initialiseRoom():
    f = open("room_details.json")
    data = json.load(f)
    f.close()
    # objects = [items['name'] for items in data["items_in_rooms"]]



    key = Item("key", "pick_up")
    door = Item("door", "open")
    table = Item("table", "look")
    objects.extend([key, door, table])

    


    # for i in data["items_in_rooms"]:
    #     objects.append(Item(i["name"], i["action"]))


# f = open('room_details.json')
# data = json.load(f)
# f.close()

# objects = [items['name'] for items in data["items_in_rooms"]]

# print("Room Created!")

def findItems(item):
    for obj in objects:
        if item == obj.getName():
            return obj
    return "No such item"

def processAction(action, subject, direct_object, indirect_object):

    item = findItems(direct_object)
    if action in vr.getSynsetsList(item.getAction()):
        current_room_items.remove(item.getName())
        bag.append(item.getName())
    
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
        while True:
  
            
            if voice_input:
                user_input = vr.recogniseSpeech()
                print("Google Speech Recognition thinks you said \"" + user_input + "\"")
            else :
                user_input = input("Waiting for input... ")
                print("Input is \"" + user_input + "\"")

            action, subject, direct_object, indirect_object = vr.processSpeech(user_input)

            processAction(action, subject, direct_object, indirect_object)

    else:
        initialiseRoom()
        print(objects)
            
    # con.close()
