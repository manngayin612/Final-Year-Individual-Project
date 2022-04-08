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
    # door.setSpecialTool("unlock", "key")
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

# def processAction(action, subject, direct_object, indirect_object):

#     item = findItems(direct_object)



#     for a in item.getActions():
#         print(a)
#         if action in vr.getSynsetsList(a):
#             if a == "pick_up":
#                 bag.append(item.getName())
#                 current_room_items.remove(item.getName())
#             elif a == "unlock":
#                 if item.getName() == "door":
#                     if objects[1].getName() in bag:
#                         item.setCurrentStatus("unlocked")
#                     else:
#                         print("The door is locked")

#             elif a == "investigate":
#                 print(item.getDescription())

        
        
#     print(current_room_items, bag)

def processAction(actions_dobjects):
    
    for (action, direct_object) in actions_dobjects:


        item = findItems(direct_object)



        for a in item.getActions():
            print(a)
            if action in vr.getSynsetsList(a):
                if a == "pick_up":
                    bag.append(item.getName())
                    current_room_items.remove(item.getName())
                elif a == "unlock":
                    if item.getName() == "door":
                        if objects[1].getName() in bag:
                            item.setCurrentStatus("unlocked")
                        else:
                            print("The door is locked")

                elif a == "investigate":
                    print(item.getDescription())

            
            
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
def doorUnlockedByKey():
    return objects[0].getCurrentStatus() == "unlocked" 

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

            actions_dobjects = vr.processSpeech(user_input)

            # processAction(action, subject, direct_object, indirect_object)
            processAction(actions_dobjects)

            success = doorUnlockedByKey()


        print("end of game")
    else:
        i = input("please input: ")
        actions_dobjects = vr.processSpeech(i)
        for i in actions_dobjects:
            print(i)
            

