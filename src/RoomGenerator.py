
import sqlite3
from regex import P

from setuptools import Require
import TextExtractor as te
import spacy
from spacy_wordnet.wordnet_annotator import WordnetAnnotator 
from nltk.corpus import wordnet as wn
from Item import CombinableItem, Item, UnlockItem
from collections import deque
import VoiceRecognitionUtils as vr
from States import States, states_dict

import time
debug = True
eval = False


# Normal items: name, item_def, actions, description
# Unlock items: name, unlock_msg, item_def, required_items, actions, unlock_action , description

def getItemDef(nlp, object):
    token = nlp(object)[0]
    item_def = ""

    domain = ["furniture", "home"]

    token._.wordnet.wordnet_domains()

    in_domain = token._.wordnet.wordnet_synsets_for_domain(domain)

    if len(in_domain)>0:
        item_def = in_domain[0].name()

    else:  
        if debug: print("Searching for hypernym")
        for ss in wn.synsets(object, pos=wn.NOUN):
            for s in ss.closure(lambda s:s.hypernyms()):
                if "physical_object" in s.lemma_names():
                    item_def = ss.name()
                    break
            else:
                continue
            break

    return object, item_def


# Returning a tuple of (change state info, new pairs description)
def createItems(state, con, cur, room_name, object, action, queue, extra_input=None):
    global item, item_def, stored_type, type, description

    unlock_msg = None
    required_item = None
    unlock_action = None

    combine_with = None
    finished_item = None
    nlp = spacy.load('en_core_web_sm')
    nlp.add_pipe(WordnetAnnotator(nlp.lang), after='tagger')

    if state == States.INPUT_PROCESS.value:
        if debug: print("Creating items with name {} and action {}".format(object, action))
        
        if  "room" in object:
            if debug: print("createItems: room ==> IGNORE")
            queue.popleft()
            return (state, (), ("", queue))
        else:
            if debug: print("createItem ==> SEARCHING DOMAIN")
            item, item_def = getItemDef(nlp, object)

        description = ""
    
        if item_def != "" : #ignore if the item is not a physical object
            if debug: print(item_def, wn.synset(item_def).definition())

            stored_type = itemExisted(cur, room_name,  item)
            if not stored_type:
                prompt = "Are you trying to add \"{}\" into the room?".format(item)
            elif stored_type != type and stored_type == "normal":
                prompt = "Are you turning a {} item, {}, into a {} item?".format(stored_type, item, type)
            else:
                prompt = "Are you updating the {} item, the {}?".format(stored_type, item)
            states_dict[States.UPDATE_STORED_ITEM] = prompt
            return (state, (prompt, False),())



    if debug: print("Said yes ", state)
    if state == States.UPDATE_STORED_ITEM.value:

        if extra_input == "yes":
            if debug: print("Stored: ", stored_type)

            if "unlock" in action or "lock" in action:
                if debug: print("Creating Unlock Item")
                # item = UnlockItem(item, unlock_msg, item_def, required_items=required_item, action=action, description=description)
                type = "unlock"
                #TODO: Special case of a numberlock

            elif "combine" in action:
                if debug: print("Creating Combinable Item")
                # item = CombinableItem(self, name, item_def, combine_with, finished_item, actions=["get", "combine"], description="")
                type = "combine"

            else:
                if debug: print("Creating Normal Item")
                # item = Item(item, item_def, description = description)
                type = "normal"

            action_query = """SELECT action FROM {} WHERE item = ?""".format(room_name)
            stored_action = cur.execute(action_query, (object,)).fetchone()
            if debug: print(stored_action)


            stored_type = itemExisted(cur, room_name,  item)
            #item didnt existed at all
            if not stored_type:
                # Giving Description to the object
                prompt = "Maybe try giving me a short description about the {}? Is it locked? Does it give any hint about other objects? Or does it contains something else?".format(object)
                print("description: ", state)
                return (state, (prompt, False), ())

            elif stored_type != type: #was initialised as normal item but its an unlock item
                if type == "normal":
                    type = stored_type
                if debug: print("Please update")
                update_record = """UPDATE {} SET type = ? WHERE item = ?""".format(room_name) 
                if debug: print("\nCONFIRMING: inserted an {} object: {}\n".format(type, object))
                cur.execute(update_record, (type, item,))
            else:
                if debug: print("got this already")

        else:
            queue.popleft()    
            return (States.INPUT_PROCESS.value,(),(description, queue))
            

    if debug: print("Before creating new item: ", state, extra_input, stored_type)
    if state == States.CREATE_NEW_ITEMS.value and not stored_type:
        description = extra_input
        if debug: print("Description: ",description)
        insert_object = """INSERT INTO {} (type, item, item_def, action, description,required_items, unlock_msg, unlock_action,  combine_with, finished_item) VALUES (?,?,?,?,?,?,?,?,?,?)""".format(room_name)
        if action == []: 
            a = None
        else:
            a = str(action)
        cur.execute(insert_object, (type, item, item_def, a, description, required_item, unlock_msg, unlock_action, combine_with, finished_item ))    
        if debug: print("\nCONFIRMING: inserted an {} object: {}\n".format(type, object))


            

    if debug: print("Check if all fields are completed. {} {}".format(item, type))

    state, change_state, new_pairs = isEntryCompleted(state+1, cur,room_name, item, type, extra_input)
    if change_state:
        prompt, _  = change_state
        return (state, (prompt, False),())

    if new_pairs:
        queue.extend(new_pairs.items())
    if debug: print("Queue: ", queue)

    con.commit()
    
    queue.popleft()
    if debug: print("Created item: ", queue, " Description: ", description)
    
    return (States.INPUT_PROCESS.value,(),(description, queue))
# else:
#     queue.popleft()
#     return "", queue


def isEntryCompleted(state, cur, room_name, item, type, extra_input=None):
    if debug: print("isEntrycompleted", state, type, item)
    global required_item, unlock_action, unlock_msg
    pair = {}
    if type == "unlock":

        if state == States.CREATE_NEW_ITEMS.value:
            if debug: print("getting entry from database")
            get_record = """SELECT required_items, unlock_msg, unlock_action FROM {} WHERE item=? and type = ?;""".format(room_name)
            result = cur.execute(get_record, (item,type,))
            row = result.fetchone()

            required_item = row[0]
            unlock_msg = row[1]
            unlock_action = row[2]
            print(required_item)
            if required_item == None:
                return (States.ASK_FOR_UNLOCK_ITEM.value-2, (states_dict[States.ASK_FOR_UNLOCK_ITEM], False),{})
    else:
        if debug: print("Everything is fine")
        return (state, (), {})

    if debug: print(state)
    if state == States.ASK_FOR_UNLOCK_ITEM.value:
        if debug: print("Check if is password or not")
        print(extra_input)
        if extra_input == "no":
            if debug: print("Filling in the unlock")
            return (States.FILL_IN_UNLOCK_ITEM.value-2, (states_dict[States.FILL_IN_UNLOCK_ITEM], False), {})
        elif extra_input == "yes":
            if debug: print("filling in password")
            return (States.FILL_IN_PASSWORD.value-2, (states_dict[States.FILL_IN_PASSWORD], False), {})
        else :
            return (States.ASK_FOR_UNLOCK_ITEM.value -2, ("Please only answer yes or no", False), {})
    
    if debug: print("after type = unlock", state)
    if state == States.FILL_IN_UNLOCK_ITEM.value:
        if debug: print("filled in object")
        pair = te.ContentExtractor(extra_input)
        if debug: print(extra_input, pair)
        (a,t) = pair[item]
        required_item = t
        unlock_action = a[0]

        if unlock_msg == None:
            return (States.CONGRATS_MSG.value-2, (states_dict[States.CONGRATS_MSG], False), {})

    elif state == States.FILL_IN_PASSWORD.value:
        if debug: print("filled in password")
        required_item = extra_input

        if debug: print('required_items: ', required_item)
        if debug: print(pair)

        if unlock_msg == None:
            return (States.CONGRATS_MSG.value-2, (states_dict[States.CONGRATS_MSG], False), {})

    if state == States.CONGRATS_MSG.value:
        if debug: print("unlock_msg: ", extra_input)
        unlock_msg = extra_input
        escaped_prob = vr.sentenceSimilarity(unlock_msg, "Congratulation! You escaped.")
        if debug: print(escaped_prob)
        if escaped_prob > 0.7:
            if debug: print("{} is the escape item".format(item))
            update_query = '''UPDATE {} SET required_items = ? WHERE item="room"'''.format(room_name)
            cur.execute(update_query, (item,))
    if required_item:
        if required_item.isdigit():
            type = "numberlock"
    if debug: print(state, type, item, required_item)
    update_query = '''UPDATE {} SET type = ?, required_items =?, unlock_msg =?, unlock_action =? WHERE item=? '''.format(room_name)
    cur.execute(update_query, (type, required_item, unlock_msg, unlock_action, item))
    if debug: print("Added to database: ", unlock_msg)
    return (state, (), pair)



        
def itemExisted(cur, room_name, item_name):
    check_exist = """SELECT type FROM {} WHERE item=?;""".format(room_name)
    result = cur.execute(check_exist, (item_name,))
    for row in result:
        return row[0]

def createRoomDatabase(name):
    con = sqlite3.connect("escaperoom.sqlite")
    cur = con.cursor()

    cur.execute('''DROP TABLE IF EXISTS {};'''.format(name))
    cur.execute('''CREATE TABLE IF NOT EXISTS {}(
        type text,
        item text, 
        item_def text,
        action text,
        description text,
        unlock_msg text,
        required_items text,
        unlock_action text,
        combine_with text, 
        finished_item text
        )'''.format(name))

    return con, cur

room_name = ""
def startGenerator(state, user_input):
    
    global con, cur, room_name, pairs_queue
    extra_input = ""

    finished = False
    nlp = spacy.load('en_core_web_sm')
    
    if state == States.NAME_ROOM.value:
        
        if debug: print("Naming the Room")
        if eval: start_time = time.process_time()
        room_name = user_input.replace(" ", "_")
        con, cur = createRoomDatabase(room_name)
        new_state = States(state+1)
        if eval: print("Create database: ", time.process_time() - start_time)
        if debug: print("DATABASE CREATED SUCCESSFULLY")
        return state+1, states_dict[new_state], finished


    if state > States.NAME_ROOM.value:
        if state == States.OVERALL_DESCRIPTION.value:
            if debug: print("Asking for general description...")
            cur.execute('''INSERT INTO {} (item, description) VALUES ("room", ?)'''.format(room_name),(user_input,))
            if eval: start_time = time.process_time()
            pairs_queue = deque((te.ContentExtractor(user_input)).items())
            if eval: print("Entire Content Extractor: ", time.process_time() - start_time)
            if debug: print(pairs_queue)

        while(not finished):
            if debug: print(state, pairs_queue)
            if len(pairs_queue)>0:
                (o,(a,t)) = pairs_queue[0]
                if debug: print("state: ", state)
                if state == States.INPUT_PROCESS.value  or state == States.UPDATE_STORED_ITEM.value or state == States.FILL_IN_UNLOCK_ITEM.value-2 or state == States.FILL_IN_PASSWORD.value-2 or  state == States.CONGRATS_MSG.value-2:
                    if debug: print(" extra_input: ", user_input)
                    extra_input = user_input
                if debug: print(o, a, pairs_queue)

                if eval: start_time = time.process_time()
                (state, change_state, new_pairs_info) = createItems(state+1, con, cur, room_name, o, a, pairs_queue, extra_input)
                if eval: print("Create Item: ", time.process_time() - start_time)

                if debug: print(change_state, new_pairs_info)
                if change_state:
                    prompt, finished = change_state
                    return state, prompt, finished
                else:
                    description_of_item, pairs_queue = new_pairs_info 
                    if eval: start_time = time.process_time()
                    newpairs = (te.ContentExtractor(description_of_item)).items()
                    pairs_queue.extendleft(newpairs)
                    if eval: print("Content Extractor: ", time.process_time() - start_time)
                    if debug: print("NEWPAIRS: ", pairs_queue)
                    user_input = ""
                    extra_input = ""
                    state = States.INPUT_PROCESS.value-1
                    
                # if debug: print(pairs_queue)
            else:
                if debug: print(state)
                if state == States.CONGRATS_MSG.value or state == States.INPUT_PROCESS.value or state == States.OVERALL_DESCRIPTION.value :
                    if debug: print("if you have anything to add?", state)
                    return States.ADD_MORE.value, states_dict[States.ADD_MORE], finished

                if state == States.ADD_MORE.value:
                    if user_input == "no":
                        finished = True
                        return state+1, states_dict[States.FINISHED], finished
                    else:
                        if debug: print("Add somthing new please: ", state)
                        return States.EXTRA_ITEM.value, states_dict[States.EXTRA_ITEM], finished

                if state == States.EXTRA_ITEM.value:
                    if debug: print("added extra item", state)
                    if eval: start_time = time.process_time()
                    newpairs = te.ContentExtractor(vr.lemmatize(nlp,user_input)).items()
                    pairs_queue.extendleft(newpairs)
                    if eval: print("Content Extractor: ", time.process_time() - start_time)
                    if debug: print("After adding Extra Item: ", pairs_queue)
                    state = States.OVERALL_DESCRIPTION.value



