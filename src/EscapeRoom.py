from random import randrange
from tkinter import Y
from tkinter.messagebox import YES
from py import process
import VoiceRecognitionUtils as vr 
from Item import CombinableItem, Item, NumberLock, UnlockItem
from Room import Room
from Input import Input
import RoomGenerator as rg
from States import States, states_dict


import json
import time

import sqlite3

from nltk.corpus import wordnet as wn
import pygame
import math
import sys
import os
import time

voice_input = False
test = False

# objects=[]
# current_room_items = ["key", "door", "table"]
# bag = []
threshold = 0.2
rooms=[]

#Initialising the game screen

pygame.init()
pygame.mixer.init()
pygame.font.init()
SQUARESIZE = 100
screen_width = 7 * SQUARESIZE
screen_height = 7 * SQUARESIZE
size = (screen_width, screen_height)

screen = pygame.display.set_mode(size)
pygame.display.set_caption("Escape Room")


font = pygame.font.SysFont("Impact", 50)
medium_font = pygame.font.SysFont("Courier", 20)
small_font = pygame.font.SysFont("Courier", 15)

button_font = pygame.font.SysFont("Rockwell", 20)

white = (255, 255, 255)
black = (0,0,0)
main_theme_color = (255,255,255)
second_theme_color = (19, 38,47)
background_color = (235, 239, 191)



def initialiseGame():

    
    open('user_input_log.txt', 'w').close()
    con = sqlite3.connect("escaperoom.sqlite")
    cur = con.cursor()

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

    buttontext = button_font.render(text, True, white)
    screen.blit(buttontext, (bg_rect[0]+(width-buttontext.get_width())/2, bg_rect[1]+(height-buttontext.get_height())))
    
def create_image_button(image, x, y, width, height):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed(3)

    img = pygame.image.load(image)
    img = pygame.transform.scale(img, (width, height))

    bg_rect = pygame.Rect(x,y,img.get_width(),img.get_height())
    pygame.draw.rect(screen, main_theme_color, bg_rect)
    
    if x + img.get_width() > mouse[0] > x and y + img.get_height() > mouse[1] > y:
        print("clicked")
        if click[0] == 1:
            return True
    screen.blit(img, bg_rect)


def blit_text(surface, text, pos, font, color=pygame.Color('black')):
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width-20:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row.



def titleScreen():
    text = font.render("Welcome to the game", True, black)

    while True:
        screen.fill(main_theme_color)
        screen.blit(text, ((screen_width - text.get_width()) /2, 50))

        # start button
        start = create_button("Start", ((screen_width-125)/2), (screen_height-35)/2, 125, 35, black, second_theme_color, medium_font)
        create = create_button("Create Room", ((screen_width-125)/2), (screen_height+50)/2, 125, 35, black, second_theme_color, medium_font)

        if start:
            playLevel(rooms[0])
        
        if create:
            createRoom()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()


def read_aloud():            
    sound_obj = pygame.mixer.Sound("speech.mp3")
    print(sound_obj.get_length())
    sound_obj.play()

    time.sleep(math.ceil(sound_obj.get_length()))

def createRoom():
    os.remove("escaperoom.sqlite")
    state = States.NAME_ROOM.value
    title_text = states_dict[States(state)]
    # title_text = medium_font.render(states_dict[States(state)], True, black)

    # Input Rectangle
    rect_width = screen_width-100
    rect_height = screen_height/4
    input_rect = pygame.Rect((screen_width-rect_width)/2, 400, rect_width, rect_height)


    file = open("room_generator_log.txt","r+")
    file.truncate(0)
    file.close()

    f = open("room_generator_log.txt", "a")


    user_input = ""
    response = ""
    yes = False
    no = False

    play_counter = 0
    
    finished = False
    while not finished:
        screen.fill(main_theme_color)
        if response == "":
            # screen.blit(title_text, (50, 200))
            blit_text(screen, title_text, (50,200), medium_font, black)
            if (play_counter == 0):
                # read_aloud()
                vr.textToSpeech(states_dict[States(state)])
                play_counter += 1
            
        mic = create_image_button("/Users/manngayin/OneDrive - Imperial College London/Fourth Year/Final Year Individual Project/images/microphone.jpeg", screen_width-250, screen_height-100, 30, 30)
        redo = create_button("REDO", screen_width-150, screen_height-100, 100, 40, (255,0,255), black, button_font)


        if mic :
            user_input = vr.recogniseSpeech()

        if redo:
            user_input = ""


        for event in pygame.event.get():
            # if event.type == pygame.QUIT:
            #     pygame.quit()
            #     sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                elif event.key == pygame.K_RETURN:
                    current_state, response, finished = rg.startGenerator(state, user_input)
                    print(current_state)
                    user_input = ""
                    
                    state = current_state
                    play_counter = 1

                else:
                    user_input +=event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                print("clicked mouse")
                if yes:
                    print("tickkkkk")
                    current_state, response, finished = rg.startGenerator(state, "yes")
                if no:
                    print("noooo")
                    current_state, response, finished = rg.startGenerator(state, "no")
                user_input = ""
                yes = False
                no = False
                
                state = current_state
                play_counter = 1



        pygame.draw.rect(screen, background_color, input_rect)


        if state in [States.INPUT_PROCESS.value, States.CREATE_NEW_ITEMS.value, States.ASK_FOR_UNLOCK_ITEM.value-1, States.FILL_IN_PASSWORD.value,10]:
            tick = create_image_button("/Users/manngayin/OneDrive - Imperial College London/Fourth Year/Final Year Individual Project/images/tick.png", input_rect.topleft[0], input_rect.topleft[1], 330, 175)
            if tick:
                yes = True
                no = False
            cross = create_image_button("/Users/manngayin/OneDrive - Imperial College London/Fourth Year/Final Year Individual Project/images/cross.png", input_rect.topright[0]/2, input_rect.topleft[1], 330,175)
            if cross:
                no = True
                yes = False


        

        blit_text(screen, user_input, input_rect.topleft, medium_font, (255,0,255))
        # text_surface = medium_font.render(user_input, True, (255, 0, 255))
        # screen.blit(text_surface,input_rect.topleft)

        blit_text(screen, response, (50,200), medium_font, black)
        if response != "":
            title_text = ""
            if play_counter == 1:
                vr.textToSpeech(response)
                play_counter += 1
        # response_text = medium_font.render(response, True, black)
        # screen.blit(response_text, (50,200))

        pygame.display.flip()
    print("end of loop")
    titleScreen()




def endingScreen(room):
    print("restarted")
    # bag = []
    # current_room_items = room.starting_items
    # print(bag, current_room_items)
    text = font.render("You escaped!", True, (255,255,255))

    while True:
        screen.fill(main_theme_color)
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

    title_text = font.render("Welcome to {}".format(room.name.replace("_", " ")), True, black)


    introduction = "Welcome to the {}. Listen up, you better be careful here. No one's here to protect you. I will give you guide, even though I don't want to. I'll tell you what's happening here, but in case you cannot hear me, open up your eyes and read it yourself. Good luck.".format(room.name.replace("_", " "))

    # vr.textToSpeech(introduction)
    # Description of the room
    description = room.description

    # Input Rectangle
    rect_width = screen_width-100
    rect_height = screen_height/4
    input_rect = pygame.Rect((screen_width-rect_width)/2, 400, rect_width, rect_height)
    
    # Input and Response
    user_input = ""
    response = ""
    play_counter = 0
    clock = pygame.time.Clock()

    # Initilise the room with objects
    con = sqlite3.connect("escaperoom.sqlite")
    cur = con.cursor()
    
    select_all = '''SELECT * FROM {} ;'''.format(room.name)
    result = cur.execute(select_all).fetchall()
    room.initialiseRoom(result)

    print("Room {} is ready with {} items in the room and {} items in the bag.".format(room.level, len(room.currentItems), len(room.bag)))
    while not room.success:
        screen.fill(main_theme_color)

        screen.blit(title_text, ((screen_width-title_text.get_width())/2, 50))
        if response == "":

            blit_text(screen, description, (50,200), medium_font, black)
            if play_counter == 0:
                vr.textToSpeech(description)
                play_counter+=1

        mic = create_image_button("/Users/manngayin/OneDrive - Imperial College London/Fourth Year/Final Year Individual Project/images/microphone.jpeg", screen_width-250, screen_height-100, 30, 30)
        redo = create_button("REDO", screen_width-150, screen_height-100, 100, 40, (255,0,255), black, button_font)


        if mic :
            user_input = vr.recogniseSpeech()

        if redo:
            user_input = ""

        for event in pygame.event.get():
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
                    play_counter = 1

                else:
                    user_input +=event.unicode
    
        pygame.draw.rect(screen, background_color, input_rect)
        # text_surface = medium_font.render(user_input, True, (255, 0, 255))
        # screen.blit(text_surface,input_rect.topleft)

        blit_text(screen, user_input, (input_rect.topleft[0]+10, input_rect.topleft[1]+10), medium_font, (255,0,255))
        
        blit_text(screen, response, (50,200), medium_font, black)
        if response != "":
            description = ""
            if play_counter == 1:
                vr.textToSpeech(response)
                play_counter += 1

        
        # response_text = small_font.render(response, True, (255,0,0))
        # screen.blit(response_text, (100,200))


        pygame.display.flip()
        clock.tick(60)
    #TODO
    print("Finished Room")
        

    endingScreen(room)
        

import spacy

if __name__ == "__main__":
    if not test:
        initialiseGame()
        print("Room Initialised.")
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


