from py import process
import VoiceRecognitionUtils as vr 
from Item import Item
import json

import nltk
# nltk.download('wordnet', force=True)
# nltk.download('omw-1.4', force=True)
from nltk.corpus import wordnet as wn
import pygame
import sys

voice_input = False
test = False
success = False
objects=[]
current_room_items = ["key", "door", "table"]
bag = []
threshold = 0.2

#Initialising the game screen
pygame.init()
SQUARESIZE = 100
width = 7 * SQUARESIZE
height = 7 * SQUARESIZE
size = (width, height)

screen = pygame.display.set_mode(size)
pygame.display.set_caption("Escape Room")


font = pygame.font.Font(pygame.font.get_default_font(), 50)
small_font = pygame.font.Font(pygame.font.get_default_font(), 10)


def initialiseRoom():
    f = open("room_details.json")
    data = json.load(f)
    f.close()

    door = Item("door", item_def="door.n.01",actions=["unlock", "open"], status=["locked", "unlocked"], action_def=["unlock.v.01",'open.v.01'], description="There is a lock on the door.")
    key = Item("key", item_def="key.n.01",action_def=["get.v.01"], actions=["get"], description="The key may be used to unlock something.")
    table = Item("table", item_def="table.n.02", description="There is a key on the table.")
    objects.extend([door, key, table])
    print("Room Created!")


# Return the Item object with the
def getItem(item_name):
    for obj in objects:
        if item_name == obj.getName():
            return obj
    return None


def identifyObject(item):
    max_similarity = 0
    matching_obj = ""
    for obj in objects:
        for ss in wn.synsets(item, pos=wn.NOUN):
            if(ss.name().split(".")[0] == item):
                current_similarity = ss.lch_similarity(wn.synset(obj.getItemDef()))
                if current_similarity > max_similarity:
                    max_similarity = current_similarity
                    matching_obj = obj
    print("Input Item: {} ==> Identified Item: {}".format(item, matching_obj.getName()))
    return matching_obj


def identifyAction(action, item):
    max_similarity = 0
    matching_action = ""
    for (a,d) in item.getActions():
        for ss in wn.synsets(action, pos=wn.VERB):
            if(ss.name().split('.')[0] == action):
                current_similarity = ss.lch_similarity(wn.synset(d)) 
                if current_similarity > max_similarity:
                    max_similarity = current_similarity
                    matching_action = a
    print("Input Action: {} ==> Identified Action: {}".format(action, matching_action))
    return matching_action if max_similarity > threshold else ""

def processAction(actions_dobjects):
    for (action, direct_object) in actions_dobjects:
        item = identifyObject(direct_object)
        matching_action = identifyAction(action, item)

        if matching_action!="":
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

        print(current_room_items, bag)

# Check if the door is unlocked 
def doorUnlockedByKey():
    return objects[0].getCurrentStatus() == "unlocked" 

def create_button(text, x, y, width, height, hovercolour, defaultcolour):
    mouse = pygame.mouse.get_pos()

    click = pygame.mouse.get_pressed(3)

    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        pygame.draw.rect(screen, hovercolour, (x,y,width, height))
        if click[0] == 1:
            firstRoom()
    else:
        pygame.draw.rect(screen, defaultcolour, (x,y,width,height))

    buttontext = small_font.render(text, True, (255,255,255))
    screen.blit(buttontext, (int(890+(width/2)), int (y + (y/2))))


def titleScreen():
    text = font.render("Welcome to the game", True, (255,255,255))

    while True:
        screen.fill((0,0,0))
        screen.blit(text, ((width - text.get_width()) /2, 0))

        # start button
        create_button("Start", width-130, 7, 125, 26, (255,255,255), (255,255,0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()

def firstRoom():
    text = font.render("Welcome to the first room", True, (255,255,255))

    while True:
        screen.fill((0,0,0))
        screen.blit(text, ((width-text.get_width())/2, 0))
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()

        




if __name__ == "__main__":
    if not test:
        


        titleScreen()
        initialiseRoom()
        while not success:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()


            pygame.display.update()

                # if event.type== pygame.KEYDOWN:

            
        #     if voice_input:
        #         user_input = vr.recogniseSpeech()
        #         print("Google Speech Recognition thinks you said \"" + user_input + "\"")
        #     else :
        #         user_input = input("Waiting for input... ")
        #         print("Input is \"" + user_input + "\"")

        #     actions_dobjects = vr.processSpeech(user_input)
           
        #     # processAction(action, subject, direct_object, indirect_object)
        #     processAction(actions_dobjects)

        #     success = doorUnlockedByKey()

        # print("end of game")
    else:
        for ss in wn.synsets("unlock", pos= wn.VERB):
            print(ss,ss.definition())

        

            

