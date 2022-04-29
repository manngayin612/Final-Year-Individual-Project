from random import randrange
from py import process
import VoiceRecognitionUtils as vr 
from Item import Item, NumberLock, UnlockItem
from Room import FirstRoom, SecondRoom
from Input import Input


import json
import time


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

def initialiseGame():
    open('user_input_log.txt', 'w').close()
    firstRoom = FirstRoom(1, [])
    secondRoom = SecondRoom(2, firstRoom.bag)
    rooms.extend([firstRoom, secondRoom])


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
                    print(ss.name(), room.items_in_room[i], current_similarity)
                    # Check hypernyms
                    wup = ss.wup_similarity(wn.synset(room.items_in_room[i].getItemDef()))

                    if current_similarity > max_similarity or wup > max_wup:
                        max_similarity = current_similarity
                        max_wup = wup
                        matching_obj_index = i
        
        identified_obj = room.items_in_room[matching_obj_index]
        print("Input Item: {} ==> Identified Item: {} ({})".format(item, identified_obj.getName(), max_similarity, max_wup))
        writeToCache(identified_obj.getName(), item)

        return identified_obj if (max_similarity > 3 or max_wup > 0.9 )else vr.generateResponse("{} is not found in the room.".format(item))


def identifyAction(action, item):
    # Check in Cache
    actionFromCache = searchCache(action)
    print(actionFromCache)
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
        return matching_action if max_similarity > threshold else vr.generateResponse("I don't think you can do this.")


def processAction(room, processed_input):
    msg = ""
    # for (action, direct_object, pw) in actions_dobjects_pw:
    start = time.process_time()
    processed_input.item = identifyObject(room, processed_input.item)
    print("Processed_input item in processAction()", processed_input.item.getActions())
    if processed_input.tool != "":
        processed_input.tool = identifyObject(room, processed_input.tool)
        print("Processed_input tools ", processed_input.tool.getName())

    if type(processed_input.item) == str:
        #TODO
        print("Lets check the next one.")
    else:
        processed_input.action = identifyAction(processed_input.action, processed_input.item)
        print(processed_input.action)

    return processed_input.item.performAction(room, processed_input)

    
def searchCache(word):
    with open("./cache.json", "r") as jsonFile:
        data = json.load(jsonFile)
        if word in data:
            return data[word]
        else:
            return ""

def writeToCache(word, new_word):
    with open("./cache.json", "r") as jsonFile:
        data = json.load(jsonFile)
        data[new_word] = word
    with open("./cache.json", "w") as jsonFile:
        json.dump(data,jsonFile)


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
    title_text = font.render(room.title, True, (255,255,255))

    # Description of the room
    description = small_font.render(room.description, True, (255,255,255))

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

    while not room.succeedCondition():
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
                    processed_inputs = vr.processSpeech(user_input)
                    for input in processed_inputs:
                        response = processAction(room,input)

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
        # Check processSpeech and processAction functions
        initialiseGame()
        rooms[0].initialiseRoom()
        print(rooms[0].items_in_room)
        # user_input = input("Input: ")
        user_input = "investigate the padlock and unlock it with 1234"
        actions_dobjects = vr.processSpeech(user_input)
        response = ""
        for i in actions_dobjects:
            response += processAction(rooms[0],i)


       # Check item.def
        # check_word = input("Check this word: ")
        # for ss in wn.synsets(check_word):
        #     print(ss.definition(), ss.name())

    
        

            

