from email.policy import default
from random import randrange
from platformdirs import user_cache_dir
from py import process
import VoiceRecognitionUtils as vr 
from Item import CombinableItem, Item, NumberLock, UnlockItem
from Room import FirstRoom, Room, SecondRoom
from Input import Input
import RoomGenerator as rg
from States import States, states_dict


import json
import time

import sqlite3

from nltk.corpus import wordnet as wn
import pygame
import sys

voice_input = False
test = True

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
    con = sqlite3.connect("escaperoom.sqlite")
    cur = con.cursor()

    #please create a room description

    select_room = '''SELECT name FROM sqlite_master WHERE type='table';'''
    result = cur.execute(select_room).fetchall()
    print("Rooms created: ",result)

    for r in result:
        room = Room(r[0], 1, [])
        select_all = '''SELECT * FROM {} ;'''.format(room.name)
        result = cur.execute(select_all).fetchall()
        room.initialiseRoom(result)
        rooms.append(room)
    print(rooms)



    # firstRoom = FirstRoom(1, [])
    # secondRoom = SecondRoom(2, firstRoom.bag)
    # rooms.extend([firstRoom, secondRoom])



def identifyObject(room, item):
    if item == "":
        item = input("What object are you interracting with?")

    #Check cache first=
    objectFromCache = searchCache(item)
    if objectFromCache != "":
        print("Got from Cache")
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
    if action == "":
        action = input("Which action do you want to perform? {}".format(item.getActions()))

    actionFromCache = searchCache(action)
    print(actionFromCache)
    if actionFromCache != "":
        print("Found action from cache")
        return actionFromCache
    elif action in item.getActions():
        return action
    else:

        max_similarity = 0
        matching_action = ""
        for assigned_action in item.getActions():

            synonyms = set([ss.name().split(".")[0] for ss in wn.synsets(assigned_action, pos=wn.VERB)])
            hypernyms = set([h.name().split(".")[0]  for ss in wn.synsets(assigned_action, pos=wn.VERB) for h in ss.hypernyms()])
            print(synonyms)
            print(hypernyms)
            if action in synonyms or action in hypernyms:
                print("Found in Synonyms or Hypernyms")
                return assigned_action
            else:
                print("Calculting similarity")
                for ss in wn.synsets(action, pos=wn.VERB):
                    for assigned_ss in wn.synsets(assigned_action, pos=wn.VERB):
                        current_similarity = ss.lch_similarity(wn.synset(assigned_ss.name())) 
                        if current_similarity > max_similarity:
                            max_similarity = current_similarity
                            matching_action = assigned_action
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


    bg_rect = pygame.Rect(x,y,width,height)
    pygame.draw.rect(screen, defaultcolour, bg_rect)

    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        bg_rect = pygame.Rect(x,y,width,height)
        pygame.draw.rect(screen, hovercolour, bg_rect)
        if click[0] == 1:
            return True

    buttontext = font.render(text, True, (0,0,255))
    screen.blit(buttontext, (bg_rect[0]+(width-buttontext.get_width())/2, bg_rect[1]+(height-buttontext.get_height())))
    


def titleScreen():
    text = font.render("Welcome to the game", True, (255,255,255))

    while True:
        screen.fill((0,0,0))
        screen.blit(text, ((screen_width - text.get_width()) /2, 50))

        # start button
        start = create_button("Start", ((screen_width-125)/2), (screen_height-35)/2, 125, 35, (255,255,255), (255,255,0), medium_font)
        create = create_button("Create Room", ((screen_width-125)/2), (screen_height+50)/2, 125, 35, (255,255,255), (255,255,0), medium_font)

        if start:
            playLevel(rooms[0])
        
        if create:
            createRoom()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()


def createRoom():
    state = States.NAME_ROOM.value
    title_text = font.render(states_dict[States(state)], True, (0, 255,255))

    # Input Rectangle
    rect_width = screen_width-100
    rect_height = screen_height/4
    input_rect = pygame.Rect((screen_width-rect_width)/2, 400, rect_width, rect_height)


    file = open("room_generator_log.txt","r+")
    file.truncate(0)
    file.close()

    f = open("room_generator_log.txt", "a")

    finished = False

    # response = rg.startGenerator(state)
    # response = font.render(response, True, (255, 255,255))
    user_input = ""
    response = ""
    
    while not finished:
        screen.fill((0,0,0))
        screen.blit(title_text, ((screen_width-title_text.get_width())/2, 50))
        # screen.blit(description, ((screen_width-description.get_width())/2, 70 + title_text.get_height()))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                elif event.key == pygame.K_RETURN:
                    current_state, response, finished = rg.startGenerator(state, user_input)
                    state = current_state

                    user_input = ""
                else:
                    user_input +=event.unicode
        
        pygame.draw.rect(screen, (255,255,0), input_rect)
        text_surface = medium_font.render(user_input, True, (255, 0, 255))
        screen.blit(text_surface,input_rect.topleft)

        
        response_text = medium_font.render(response, True, (255,0,0))
        screen.blit(response_text, (100,200))

        pygame.display.flip()



def endingScreen(room):
    print("restarted")
    # bag = []
    # current_room_items = room.starting_items
    # print(bag, current_room_items)
    text = font.render("You escaped!", True, (255,255,255))

    while True:
        screen.fill((0,0,0))
        screen.blit(text, ((screen_width - text.get_width()) /2, 50))

        # start button
        try_again_button = create_button("Try again", ((screen_width-125)/2), (screen_height-35)/2, 200, 50, (255,255,255), (255,255,0), medium_font)
        next_level_button = create_button("Next Level", ((screen_width-125)/2), (screen_height+150)/2, 200, 50, (255,255,255), (255,255,0), medium_font)
        
        if try_again_button:
            playLevel(rooms[room.level-1])
        elif next_level_button:
            playLevel(rooms[room.level])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()

# Content of the first room
def playLevel(room):
    # Title of the room

    title_text = font.render("Welcome to {}".format(room.name.replace("_", " ")), True, (255,255,255))

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
    con = sqlite3.connect("escaperoom.sqlite")
    cur = con.cursor()
    
    select_all = '''SELECT * FROM {} ;'''.format(room.name)
    result = cur.execute(select_all).fetchall()
    room.initialiseRoom(result)

    print("Room {} is ready with {} items in the room and {} items in the bag.".format(room.level, len(room.currentItems), len(room.bag)))
    while not room.success:
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
                    processed_inputs = vr.processSpeech( user_input)
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
    print("Finished Room")
        

    endingScreen(room)
        

import spacy

if __name__ == "__main__":
    if not test:
        initialiseGame()
        titleScreen()

    else:
        # Check processSpeech and processAction functions
        # initialiseGame()
        # rooms[1].initialiseRoom()
        # print(rooms[1].items_in_room)
        # # user_input = input("Input: ")

        # while True:
        #     user_input = input("Input: ")
        #     actions_dobjects = vr.processSpeech(user_input)
        #     response = ""
        #     for i in actions_dobjects:
        #         response += processAction(rooms[1],i)


    # Check item.def
        # check_word = input("Check this word: ")
        # print(wn.synsets("pick"))
        # for ss in wn.synsets("pick", pos=wn.VERB):
        #     print(ss.hypernyms()[0])

        #     hypernym = ss.hypernyms()[0]


        # print([str(hypernyms.name().split(".")[0]) for hypernyms in wn.synsets("pick").hypernyms()])

        # print([h.name().split(".")[0]  for ss in wn.synsets("pick", pos=wn.VERB) for h in ss.hypernyms()])
        # print([ss.name().split(".")[0] for ss in wn.synsets("pick", pos=wn.VERB)])
        state = States.NAME_ROOM.value
        user_input = "Dark Hole"
        response = ""
        finished = False
        while not finished:
            current_state, response, finished = rg.startGenerator(state, user_input)
            state = current_state
            if state != States.FINISHED.value:
                user_input = input(response)
            print(finished)


