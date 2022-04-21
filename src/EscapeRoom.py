from random import randrange
from py import process
import VoiceRecognitionUtils as vr 
from Item import Item
from Room import FirstRoom
import ChatGenerator 
import json
import time

import nltk
# nltk.download('wordnet', force=True)
# nltk.download('omw-1.4', force=True)
from nltk.corpus import wordnet as wn
import pygame
import sys

voice_input = False
test = False

# objects=[]
# current_room_items = ["key", "door", "table"]
# bag = []
threshold = 0.2
rooms=[]

#Initialising the game screen
pygame.init()
SQUARESIZE = 100
screen_width = 7 * SQUARESIZE
screen_height = 7 * SQUARESIZE
size = (screen_width, screen_height)

screen = pygame.display.set_mode(size)
pygame.display.set_caption("Escape Room")


font = pygame.font.Font(pygame.font.get_default_font(), 50)
medium_font = pygame.font.Font(pygame.font.get_default_font(), 30)
small_font = pygame.font.Font(pygame.font.get_default_font(), 15)

# def initialiseRoom():
#     door = Item("door", item_def="door.n.01",actions=["unlock", "open"], status=["locked", "unlocked"], action_def=["unlock.v.01",'open.v.01'], description="There is a lock on the door.")
#     key = Item("key", item_def="key.n.01",action_def=["get.v.01"], actions=["get"], description="The key may be used to unlock something.")
#     table = Item("table", item_def="table.n.02", description="There is a key on the table.")
#     objects.extend([door, key, table])
#     print("Room Created!")

def initialiseGame():
    firstRoom = FirstRoom(1, [])
    rooms.append(firstRoom)


def identifyObject(room, item):
    #Check cache first=
    objectFromCache = searchCache(item)
    if objectFromCache != "":
        for i in room.items_in_room:
            if i.getName() == objectFromCache:
                return i
    else:
        max_similarity = 0
        max_wup = 0
        matching_obj_index = -1
        for i in range(len(room.items_in_room)):
            for ss in wn.synsets(item, pos=wn.NOUN):
                if(ss.name().split(".")[0] == item):
                    # Check synonyms
                    current_similarity = ss.lch_similarity(wn.synset(room.items_in_room[i].getItemDef()))
                    # Check hypernyms
                    wup = ss.wup_similarity(wn.synset(room.items_in_room[i].getItemDef()))

                    if current_similarity > max_similarity or wup > max_wup:
                        max_similarity = current_similarity
                        max_wup = wup
                        matching_obj_index = i
        
        identified_obj = room.items_in_room[matching_obj_index]
        print("Input Item: {} ==> Identified Item: {} ({})".format(item, identified_obj.getName(), max_similarity, max_wup))
        writeToCache(identified_obj.getName(), item)
        return identified_obj if (max_similarity > 3 or wup > 0.9 )else generateResponse("{} is not found in the room.".format(item))


def identifyAction(action, item):
    # Check in Cache
    actionFromCache = searchCache(action)
    if actionFromCache != "":
        return actionFromCache
    else:
        max_similarity = 0
        matching_action = ""
        for (a,d) in item.getActions():
            for ss in wn.synsets(action, pos=wn.VERB):
                
                # if(ss.name().split('.')[0] == action):
                    
                current_similarity = ss.lch_similarity(wn.synset(d)) 
                if current_similarity > max_similarity:
                    max_similarity = current_similarity
                    matching_action = a
        print("Input Action: {} ==> Identified Action: {}".format(action, matching_action))
        writeToCache(matching_action, action)
        return matching_action if max_similarity > threshold else generateResponse("I don't think you can do this.")

def processAction(room, actions_dobjects):
    msg = ""
    for (action, direct_object) in actions_dobjects:
        start = time.process_time()
        item = identifyObject(room, direct_object)

        if type(item) == str:
            #TODO
            print("Lets check the next one.")
            continue
        else:
            matching_action = identifyAction(action, item)

        if matching_action!="":
            if matching_action == "get":
                room.bag.append(item.getName())
                room.currentItems.remove(item.getName())
                msg += generateResponse("You have got {} in your bag.".format(item.getName()))
            elif matching_action == "unlock":
                print("Matched Action")
                if item.getName() == "door":
                    if "key" in room.bag:
                        item.setCurrentStatus("unlocked")
                        msg+= generateResponse("The door is unlocked.")
                    else:
                        msg+= generateResponse("The door is locked.")

            elif matching_action == "investigate":
                msg+= item.getDescription()
        elapsed = time.process_time() - start
        print(elapsed)
    return msg

def searchCache(word):
    with open("cache.json", "r") as jsonFile:
        data = json.load(jsonFile)
        if word in data:
            return data[word]
        else:
            return ""

def writeToCache(word, new_word):
    with open("cache.json", "r") as jsonFile:
        data = json.load(jsonFile)

        data[new_word] = word
    with open("cache.json", "w") as jsonFile:
        json.dump(data,jsonFile)

def generateResponse(res):
    num_beams = 30
    num_return_sequences = 20
    responses = ChatGenerator.get_response(res,num_return_sequences,num_beams)
    index = randrange(len(responses))
    print(res, "--", responses[index])
    return responses[index]




def create_button(text, x, y, width, height, hovercolour, defaultcolour, font):
    mouse = pygame.mouse.get_pos()

    click = pygame.mouse.get_pressed(3)

    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        pygame.draw.rect(screen, hovercolour, (x,y,width, height))
        if click[0] == 1:
            playLevel(rooms[0])
    else:
        pygame.draw.rect(screen, defaultcolour, (x,y,width,height))

    buttontext = font.render(text, True, (0,0,255))
    screen.blit(buttontext, ((screen_width-buttontext.get_width())/2, (screen_height-buttontext.get_height())/2))


def titleScreen():
    text = font.render("Welcome to the game", True, (255,255,255))

    while True:
        screen.fill((0,0,0))
        screen.blit(text, ((screen_width - text.get_width()) /2, 50))

        # start button
        create_button("Start", ((screen_width-125)/2), (screen_height-35)/2, 125, 35, (255,255,255), (255,255,0), medium_font)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()


def endingScreen():
    print("restarted")
    bag = []
    current_room_items = ["key", "door", "table"]
    print(bag, current_room_items)
    text = font.render("You escaped!", True, (255,255,255))

    while True:
        screen.fill((0,0,0))
        screen.blit(text, ((screen_width - text.get_width()) /2, 50))

        # start button
        create_button("Try again", ((screen_width-125)/2), (screen_height-35)/2, 125, 35, (255,255,255), (255,255,0), medium_font)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()

# Content of the first room
def playLevel(room):
    # Title of the room
    title_text = font.render("Welcome to the first room", True, (255,255,255))

    # Description of the room
    description = small_font.render("There is a key on the table. The door is locked.", True, (255,255,255))

    # Input Rectangle
    rect_width = screen_width-100
    rect_height = screen_height/4
    input_rect = pygame.Rect((screen_width-rect_width)/2, 400, rect_width, rect_height)
    
    # Input and Response
    user_input = ""
    response = ""
    clock = pygame.time.Clock()

    # Initilise the room with objects
    room.initialiseRoom()
    print("Room {} is ready with {} items in the room and {} items in the bag.".format(room.level, len(room.currentItems), len(room.bag)))

    while not room.doorUnlocked():
        screen.fill((0,0,0))
        screen.blit(title_text, ((screen_width-title_text.get_width())/2, 50))
        screen.blit(description, ((screen_width-description.get_width())/2, 70 + title_text.get_height()))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            #TODO: is there a way to switch between voice and keyboard more freely?
            if event.type == pygame.MOUSEBUTTONDOWN:
                (mouse_x, mouse_y) = pygame.mouse.get_pos()
                if input_rect.collidepoint(mouse_x, mouse_y):
                    user_input = vr.recogniseSpeech()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                elif event.key == pygame.K_RETURN:

                    print(user_input)
                    actions_dobjects = vr.processSpeech(user_input)
                    response = processAction(room,actions_dobjects)

                    user_input = ""

                else:
                    user_input +=event.unicode

        pygame.draw.rect(screen, (255,255,0), input_rect)
        text_surface = medium_font.render(user_input, True, (255, 0, 255))
        screen.blit(text_surface,input_rect.topleft)

        
        response_text = medium_font.render(response, True, (255,0,0))
        screen.blit(response_text, (100,200))

        pygame.display.flip()
        clock.tick(60)


    #TODO
        

    endingScreen()
        


if __name__ == "__main__":
    if not test:
        initialiseGame()
        titleScreen()

    else:
        initialiseGame()
        rooms[0].initialiseRoom()
        user_input = input("Input: ")
        actions_dobjects = vr.processSpeech(user_input)
        response = processAction(rooms[0],actions_dobjects)
        generateResponse(response)
    
        

            

