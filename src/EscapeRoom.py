from py import process
import VoiceRecognitionUtils as vr 
from Item import Item
import json

import nltk
# nltk.download('wordnet', force=True)
# nltk.download('omw-1.4', force=True)
from nltk.corpus import wordnet as wn

voice_input = False
test = False
success = False
objects=[]
current_room_items = ["key", "door", "table"]
bag = []
threshold = 0.2

def initialiseRoom():
    f = open("room_details.json")
    data = json.load(f)
    f.close()


    # Set up items in the room
    door = Item("door", actions=["unlock", "open"], status=["locked", "unlocked"], definition=["unlock.v.01",'open.v.01'])
    # door.setSpecialTool("unlock", "key")
    key = Item("key", definition=["get.v.01"], actions=["get"])
    table = Item("table")
    objects.extend([door, key, table])
    print("Room Created!")


# See if the item exists in the room
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

# Takes in a list of tuples (action, direct object) and carry out the action
# def processAction(actions_dobjects):
    
#     for (action, direct_object) in actions_dobjects:

#         item = findItems(direct_object)

#         for (a,d) in item.getActions():
#             print(a,d)
#             if a in vr.getSynsetsList(action):
  
#                 if a == "get": # only append to bag when picking up things
#                     bag.append(item.getName())
#                     current_room_items.remove(item.getName())
#                 elif a == "unlock":
#                     if item.getName() == "door": # update status of the door when unlocking it
#                         if objects[1].getName() in bag:
#                             item.setCurrentStatus("unlocked")
#                         else:
#                             print("The door is locked")

#                 elif a == "investigate": # return description of the item when investigate
#                     print(item.getDescription())

#         print(current_room_items, bag)


def processAction(actions_dobjects):
    
    for (action, direct_object) in actions_dobjects:
        max_similarity = 0
        matching_action = ""
        item = findItems(direct_object) 

        for (a,d) in item.getActions():
            print(a,d)
            for ss in wn.synsets(action, pos=wn.VERB):
                if(ss.name().split('.')[0] == action):
                    current_similarity = ss.lch_similarity(wn.synset(d)) 
                    if current_similarity > max_similarity:
                        max_similarity = current_similarity
                        matching_action = a
        if max_similarity > threshold:
            if matching_action == "get":
                bag.append(item.getName())
                current_room_items.remove(item.getName())
            elif matching_action == "unlock":
                if item.getName() == "door":
                    if objects[1].getName() in bag:
                        item.setCurrentStatus("unlocked")
                    else:
                        print("The door is locked")
            elif matching_action == "investigate":
                print(item.getDescription())







            # if a in vr.getSynsetsList(action):
  
            #     if a == "get": # only append to bag when picking up things
            #         bag.append(item.getName())
            #         current_room_items.remove(item.getName())
            #     elif a == "unlock":
            #         if item.getName() == "door": # update status of the door when unlocking it
            #             if objects[1].getName() in bag:
            #                 item.setCurrentStatus("unlocked")
            #             else:
            #                 print("The door is locked")

            #     elif a == "investigate": # return description of the item when investigate
            #         print(item.getDescription())

        print(current_room_items, bag)

# Check if the door is unlocked 
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
        for ss in wn.synsets("investigate", pos= wn.VERB):
            print(ss,ss.definition())
        
        # print(set([lemma for s in wn.synsets("get", pos = wn.VERB) for lemma in s.lemma_names()]))
        # print(wn.synset("get.v.01").path_similarity(wn.synset("contract.v.04")))
        # print(wn.synset("get.v.01").path_similarity(wn.synset("grab.v.05")))
        # print(wn.synset("get.v.01").path_similarity(wn.synset("take.v.04")))
        

            

