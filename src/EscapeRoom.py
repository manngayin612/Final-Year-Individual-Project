import VoiceRecognitionUtils as vr 
from Room import Room
import RoomGenerator as rg
from States import States, states_dict

import sqlite3

from nltk.corpus import wordnet as wn
import pygame
import sys




threshold = 0.2
cache_size = 5
cache = []
rooms=[]

debug = False
test = False
room_to_play = "./room_database/demo2.sqlite"


# Initialising game screen
pygame.init()
pygame.mixer.init()
pygame.font.init()

# Variables for the pygame screen
SQUARESIZE = 100
screen_width = 7 * SQUARESIZE
screen_height = 7 * SQUARESIZE
size = (screen_width, screen_height)

screen = pygame.display.set_mode(size)
pygame.display.set_caption("Voice Recognition Escape Room")

# Fonts
font = pygame.font.Font("orange juice 2.0.ttf", 65)
medium_font = pygame.font.SysFont("Courier", 20)
small_font = pygame.font.SysFont("Courier", 15)
button_font = pygame.font.Font("BiteBullet.ttf", 45)

# Colours
white = (255, 255, 255)
black = (0,0,0)
main_theme_color = (255,255,255)
yellow = (249,220, 92, 50)
red = (144, 78, 85, 30)



# Connect to SQLite Database and initialise rooms
def initialiseGame():
    open('user_input_log.txt', 'w').close()
    con = sqlite3.connect(room_to_play)
    cur = con.cursor()

    select_room = '''SELECT name FROM sqlite_master WHERE type='table';'''
    result = cur.execute(select_room).fetchall()

    for r in result:
        room = Room(r[0], 1, [])
        select_all = '''SELECT * FROM {} ;'''.format(room.name)
        result = cur.execute(select_all).fetchall()
        room.initialiseRoom(result)
        rooms.append(room)
    if debug: print(rooms)


# Identify item as room objects
def identifyObject(room, item):
    if item == "":
        return "I am not sure which item are you referring to, can you try again?"

    # Cache Search
    objectFromCache = searchCache(item)
    if objectFromCache != "":
        if debug: print("Got from Cache")
        for i in room.items_in_room:
            if i.getName() == objectFromCache:
                return i
    else:
        max_similarity = 0
        matching_obj_index = -1
        for i in range(len(room.items_in_room)):
            # Check if in synonyms or hypernyms list
            if vr.isSimilarWord(room.items_in_room[i].getName(), item, "n"):
                if debug: print(item, room.items_in_room[i].getName(), {"found in synonyms or hypernyms"})
                writeToCache(room.items_in_room[i].getName(), item)
                return room.items_in_room[i]
            else:
                # Check similarity scores
                for ss in wn.synsets(item, pos=wn.NOUN):
                    if(ss.name().split(".")[0] == item):
                        current_similarity = ss.lch_similarity(wn.synset(room.items_in_room[i].getItemDef()))
                        if debug: print("Similarity check: ", room.items_in_room[i], current_similarity)
                        if current_similarity > max_similarity :
                            max_similarity = current_similarity
                            matching_obj_index = i
            
                identified_obj = room.items_in_room[matching_obj_index]
                
        if debug: print("Input Item: {} ==> Identified Item: {} ({})".format(item, identified_obj.getName(), max_similarity))

        # Write to cache if a pair is found
        if max_similarity > 1.8:
            writeToCache(identified_obj.getName(), item)
            return identified_obj
        else:
            return "{} is not found in the room".format(item)


# Identify the input action from the items' available input
def identifyAction(action, item):
    # Check in Cache
    if action == "":
        return ""

    actionFromCache = searchCache(action)
    if actionFromCache != "":
        return actionFromCache
    elif action in item.getActions():
        return action
    else:

        max_similarity = 0
        matching_action = ""
        for assigned_action in item.getActions():
            # Search in synonyms or hypernyms list
            if vr.isSimilarWord(assigned_action, action,"v"):
                if debug: print("Found in Synonyms or Hypernyms")
                return assigned_action
            else:
                # Calculate similarity scores
                if debug: print("Calculting similarity")
                for ss in wn.synsets(action, pos=wn.VERB):
                    for assigned_ss in wn.synsets(assigned_action, pos=wn.VERB):
                        current_similarity = ss.lch_similarity(wn.synset(assigned_ss.name())) 
                        if current_similarity > max_similarity:
                            max_similarity = current_similarity
                            matching_action = assigned_action
        if debug: print("Input Action: {} ==> Identified Action: {}".format(action, matching_action))
        if max_similarity > threshold:
            writeToCache(matching_action, action)
            return matching_action
        else:
            ""

# Match the object and action to existing room object, and perform identified action on the item
def processAction(room, processed_input):
    identified_item = identifyObject(room, processed_input.item)
    if isinstance(identified_item, str):
        return identified_item
    else:
        processed_input.item = identified_item
    
    if processed_input.tool != "":
        processed_input.tool = identifyObject(room, processed_input.tool)

    identified_action = identifyAction(processed_input.action, processed_input.item)
    if identified_action == "":
        return "Can you try again specifying the action you want to perform?"
    else:
        processed_input.action = identified_action

    return processed_input.item.performAction(room , processed_input)

    
def searchCache(word):
    for (new_word, stored_word) in cache:
        if new_word == word:
            return stored_word
    return ""

def writeToCache(word, new_word):
    cache.insert(len(cache)-1, (new_word, word))
    if len(cache) > cache_size:
        cache.pop()

#-------------------Pygame Utils-----------------------#
# Create text button in pygame
def create_button(text, x, y, width, height, hovercolour):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed(3)


    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        bg_rect = pygame.Rect(x,y+30,width-50,8)
        pygame.draw.rect(screen, hovercolour, bg_rect)
        if click[0] == 1:
            return True

    buttontext = button_font.render(text, True, black)
    screen.blit(buttontext, (x, y))
    
# Create image button in pygame
def create_image_button(image, x, y, width, height):

    img = pygame.image.load(image)
    img = pygame.transform.scale(img, (width, height))

    bg_rect = pygame.Rect(x,y,img.get_width(),img.get_height())
    pygame.draw.rect(screen, main_theme_color, bg_rect)

    screen.blit(img, bg_rect)
    return img.get_rect(topleft=(x,y))


# Displaying text and move to next line automatically if it exceeded the defined width
def blit_text(surface, text, pos, font, color=pygame.Color('black')):
    words = [word.split(' ') for word in text.splitlines()]
    space = font.size(' ')[0]
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width-70:
                x = pos[0]  
                y += word_height
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]
        y += word_height 



def titleScreen():
    text = font.render("Are you ready to escape?", True, black)
    bg_image = pygame.image.load('./images/exit.png')
    bg_image = pygame.transform.scale(bg_image, (230, 230))

    while True:

        screen.fill(main_theme_color)
        screen.blit(bg_image, (225,275))
        screen.blit(text, ((screen_width - text.get_width()) /2, 50))

        # start button
        start = create_button("Start", 50, (screen_height-35)/2, 125, 35, yellow)
        create = create_button("Create", screen_width-150, (screen_height-35)/2, 125, 35, yellow)

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
    # os.remove("escaperoom.sqlite")
    state = States.NAME_ROOM.value
    title_text = states_dict[States(state)]

    # Creating the input rectangle for user input
    rect_width = screen_width-100
    rect_height = screen_height/4

    input_rect = pygame.image.load("./images/speechbox.png")
    input_rect = pygame.transform.scale(input_rect, (rect_width, rect_height))
    input_rect_surface = input_rect.get_rect()
    input_rect_x = (screen_width-rect_width)/2
    input_rect_y = 400
    
    # Creating the log file for room generator
    file = open("room_generator_log.txt","r+")
    file.truncate(0)
    file.close()

    f = open("room_generator_log.txt", "a")

    user_input = ""
    response = ""
    tick_img = None
    cross_img = None

    play_counter = 0
    
    finished = False
    while not finished:
        screen.fill(main_theme_color)
        if response == "":
            blit_text(screen, title_text, (50,200), medium_font, black)
            if (play_counter == 0):
                vr.textToSpeech(states_dict[States(state)])
                play_counter += 1
            
        mic = create_image_button("/Users/manngayin/OneDrive - Imperial College London/Fourth Year/Final Year Individual Project/images/microphone.jpeg", screen_width-250, screen_height-100, 40, 40)
        redo = create_button("REDO", screen_width-150, screen_height-100, 100, 40, red)

        if redo:
            user_input = ""

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                elif event.key == pygame.K_RETURN:
                    current_state, response, finished = rg.startGenerator(state, user_input)
                    if debug: print(current_state)
                    user_input = ""
                    state = current_state
                    play_counter = 1

                else:
                    user_input +=event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                (x, y) = event.pos

                # Creating yes/no buttons
                if tick_img:
                    if tick_img.collidepoint(x,y) and state in [States.INPUT_PROCESS.value, States.CREATE_NEW_ITEMS.value, States.FILL_IN_PASSWORD.value, States.ADD_MORE.value]:
                        current_state, response, finished = rg.startGenerator(state, "yes")
                        state = current_state
                        play_counter = 1
                        
                        
                if cross_img and state in [States.INPUT_PROCESS.value, States.CREATE_NEW_ITEMS.value,  States.FILL_IN_PASSWORD.value, States.ADD_MORE.value]:
                    if cross_img.collidepoint(x,y):
                        current_state, response, finished = rg.startGenerator(state, "no")
                        state = current_state
                        play_counter = 1
                

                if mic.collidepoint(x,y):
                    user_input = vr.recogniseSpeech()
                    print(user_input)
                    if user_input is None:
                        user_input = ""
                        response = "I can't hear you, can you try again?"
    
        screen.blit(input_rect,(input_rect_x, input_rect_y) )

        if state in [States.INPUT_PROCESS.value, States.CREATE_NEW_ITEMS.value,10 ]:
            tick_img = create_image_button("/Users/manngayin/OneDrive - Imperial College London/Fourth Year/Final Year Individual Project/images/tick.png", input_rect_x, input_rect_y, 330, 175)
            cross_img = create_image_button("/Users/manngayin/OneDrive - Imperial College London/Fourth Year/Final Year Individual Project/images/cross.png", input_rect_x+300, input_rect_y, 330,175)

        blit_text(screen, user_input, (input_rect_x+50, input_rect_y +10), medium_font, (255,0,255))
        blit_text(screen, response, (50,200), medium_font, black)

        # Read the response out loud
        if response != "":
            title_text = ""
            if play_counter == 1:
                # vr.textToSpeech(vr.generateResponse(response))
                vr.textToSpeech(response)
                play_counter += 1

        pygame.display.flip()
    if debug: print("end of loop")
    titleScreen()


# Playing the game
def playLevel(room):
    title_text = font.render("Welcome to {}".format(room.name.replace("_", " ")), True, black)
    introduction = "Welcome to the {}. Listen up, you better be careful here because no one's here to protect you. Good luck.".format(room.name.replace("_", " "))
    vr.textToSpeech(introduction)

    description = room.description

    # Input Rectangle
    rect_width = screen_width-100
    rect_height = screen_height/4
    input_rect = pygame.image.load("./images/speechbox.png")
    input_rect = pygame.transform.scale(input_rect, (rect_width, rect_height))
    
    # Input and Response
    user_input = ""
    response = ""
    play_counter = 0
    clock = pygame.time.Clock()
    
    if debug: print("Room {} is ready with {} items in the room and {} items in the bag.".format(room.level, len(room.currentItems), len(room.bag)))

    # Starting game loop
    while not room.success:
        screen.fill(main_theme_color)
        screen.blit(title_text, ((screen_width-title_text.get_width())/2, 50))

        blit_text(screen, description, (50,200), medium_font, black)
        if play_counter == 0:
            # vr.textToSpeech(vr.generateResponse(description))
            vr.textToSpeech(description)
            play_counter+=1

        mic = create_image_button("/Users/manngayin/OneDrive - Imperial College London/Fourth Year/Final Year Individual Project/images/microphone.jpeg", screen_width-250, screen_height-100, 40, 40)
        redo = create_button("REDO", screen_width-150, screen_height-100, 100, 40, red)

        if redo:
            user_input = ""

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                elif event.key == pygame.K_RETURN:
                    # Start processing the input once the user pressed enter
                    processed_inputs = vr.processSpeech(user_input)
                    
                    for input in processed_inputs:
                        response = processAction(room,input)
                    user_input = ""
                    play_counter = 1
                else:
                    user_input +=event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                (x,y) = event.pos

                if mic.collidepoint(x,y):
                    user_input  = vr.recogniseSpeech()
                    if user_input is None:
                        user_input = ""
                        response = "I can't hear you, can you try again?"
    
        screen.blit(input_rect,((screen_width-rect_width)/2, 400) )
        blit_text(screen, user_input, ((screen_width-rect_width)/2+50, 410), medium_font, (255,0,255))
        blit_text(screen, response, (50,300), medium_font, black)

        # Read the response out loud
        if response != "":
            if play_counter == 1:
                # vr.textToSpeech(vr.generateResponse(response))
                vr.textToSpeech(response)
                play_counter += 1

        pygame.display.flip()
        clock.tick(60)
        room.success = room.succeedCondition()
    if debug: print("Finished Room")
        
    endingScreen(room)
        

def endingScreen(room):
    if debug: print("restarted")

    text = font.render("You escaped!", True, (255,255,255))

    while True:
        screen.fill(main_theme_color)
        screen.blit(text, ((screen_width - text.get_width()) /2, 50))

        # start button
        try_again_button = create_button("Try again", ((screen_width-125)/2), (screen_height-35)/2, 200, 50, (255,255,255))
        next_level_button = create_button("Next Level", ((screen_width-125)/2), (screen_height+150)/2, 200, 50, (255,255,255))
        
        if try_again_button:
            playLevel(rooms[room.level-1])
        elif next_level_button:
            playLevel(rooms[room.level])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()



if __name__ == "__main__":
    if not test:
        initialiseGame()
        if debug: print("Room Initialised.")
        titleScreen()

    # else:
        # Check processSpeech and processAction functions
        # initialiseGame()
        # rooms[1].initialiseRoom()
        # if debug: print(rooms[1].items_in_room)
        # # user_input = input("Input: ")

        # while True:
        #     user_input = input("Input: ")
        #     actions_dobjects = vr.processSpeech(user_input)
        #     response = ""
        #     for i in actions_dobjects:
        #         response += processAction(rooms[1],i)


        # nlp = spacy.load("en_core_web_sm")
        # user_input = "look at the dog"
        # doc = nlp(user_input)
        # for t in doc:
        #     print(t.text, t.dep_, t.pos_, t.head.text)

    # Check item.def
        # check_word = input("Check this word: ")


        # for ss in wn.synsets("painting", pos=wn.NOUN):
        #     if ss.name().split(".")[0] == "painting":
        #         print(wn.synsets("painting"))
        # stored_word = "painting"

        # synonyms = set([ss.name().split(".")[0] for ss in wn.synsets(stored_word, pos=wn.NOUN)])
        # hypernyms = set([h.name().split(".")[0]  for ss in wn.synsets(stored_word, pos=wn.NOUN) for h in ss.hypernyms()])
        # print(synonyms)
        # print(hypernyms)
        # state = States.NAME_ROOM.value
        # user_input = "Dark Hole"
        # response = ""
        # finished = False
        # while not finished:
        #     current_state, response, finished = rg.startGenerator(state, user_input)
        #     state = current_state
        #     if state != States.FINISHED.value:
        #         user_input = input(response)
        #     if debug: print(finished)


