import sqlite3
import TextExtractor as te
import spacy
from spacy_wordnet.wordnet_annotator import WordnetAnnotator 
from nltk.corpus import wordnet as wn
from Item import CombinableItem, Item, UnlockItem
from collections import deque
import VoiceRecognitionUtils as vr


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
        print("Searching for hypernym")
        for ss in wn.synsets(object, pos=wn.NOUN):
            for s in ss.closure(lambda s:s.hypernyms()):
                if "physical_object" in s.lemma_names():
                    item_def = ss.name()
                    break
            else:
                continue
            break

    return object, item_def



def createItems(con, cur, room_name, object, action, queue):

    nlp = spacy.load('en_core_web_sm')
    nlp.add_pipe(WordnetAnnotator(nlp.lang), after='tagger')

    # print("Item Existed? ", itemExisted(cur, object, "normal"))

    # if not itemExisted(cur, object):
    print("Creating items with name {} and action {}".format(object, action))
        
    if  "room" in object:
        print("createItems: room ==> IGNORE")
        queue.popleft()
        return "", queue
    else:
        print("createItem ==> SEARCHING DOMAIN")
        item, item_def = getItemDef(nlp, object)

    description = ""
    
    


    if item_def != "" : #ignore if the item is not a physical object
        print(item_def, wn.synset(item_def).definition())

        unlock_msg = None
        required_item = None
        unlock_action = None

        combine_with = None
        finished_item = None


        stored_type = itemExisted(cur, room_name,  item)
        if not stored_type:
            prompt = "Is \"{}\" something you want to add into the room?".format(item)
        else:
            prompt = "Is this updates to the \"{}\"?".format(item)
        user_input = input(prompt)
        if not (vr.sentenceSimilarity(user_input, "no") > 0.9):

            print("Stored: ", stored_type)

            if "unlock" in action or "lock" in action:
                print("Creating Unlock Item")
                # item = UnlockItem(item, unlock_msg, item_def, required_items=required_item, action=action, description=description)
                #Store it into SQL
                type = "unlock"
                #TODO: Special case of a numberlock

            elif "combine" in action:
                print("Creating Combinable Item")
                # item = CombinableItem(self, name, item_def, combine_with, finished_item, actions=["get", "combine"], description="")
                type = "combine"

            else:
                print("Creating Normal Item")
                # item = Item(item, item_def, description = description)
                type = "normal"

            action_query = """SELECT action FROM {} WHERE item = ?""".format(room_name)
            stored_action = cur.execute(action_query, (object,)).fetchone()
            print(stored_action)
            # more_info = input("Do you have anymore information to add? ")
            # new_pairs = te.ContentExtractor(more_info)


            

            #item didnt existed at all
            if not stored_type:
                # Giving Description to the object
                description = input("Short description for {}: ".format(object))

                insert_object = """INSERT INTO {} (type, item, item_def, action, description,required_items, unlock_msg, unlock_action,  combine_with, finished_item) VALUES (?,?,?,?,?,?,?,?,?,?)""".format(room_name)
                if action == []: 
                    a = None
                else:
                    a = str(action)
                cur.execute(insert_object, (type, item, item_def, a, description, required_item, unlock_msg, unlock_action, combine_with, finished_item ))    
                print("\nCONFIRMING: inserted an {} object: {}\n".format(type, object))
            elif stored_type != type: #was initialised as normal item but its an unlock item
                print("Please update")
                update_record = """UPDATE {} SET type = ? WHERE item = ?""".format(room_name) 
                print("\nCONFIRMING: inserted an {} object: {}\n".format(type, object))
                cur.execute(update_record, (type, item,))
            else:
                print("got this already")


            print("Check if all fields are completed.")
            new_pairs = isEntryCompleted(cur,room_name, item, type)
            if new_pairs:
                queue.extend(new_pairs.items())
            print(queue)

            con.commit()
        
    queue.popleft()
    print("Created item: ", queue, "\n")
    return description, queue
# else:
#     queue.popleft()
#     return "", queue


def isEntryCompleted(cur, room_name, item, type):
    pair = {}
    if type == "unlock":
        get_record = """SELECT required_items, unlock_msg, unlock_action FROM {} WHERE item=? and type = ?;""".format(room_name)
        result = cur.execute(get_record, (item,type,))
        row = result.fetchone()

        required_item = row[0]
        unlock_msg = row[1]
        unlock_action = row[2]

        if required_item == None:
            user_input = input("How do you unlock this item?")
            pair = te.ContentExtractor(user_input)
            (a,t) = pair[item] 
            required_item = t
            unlock_action = a[0]
            print(pair)


        if unlock_msg == None:
            user_input = input("What do you want to say to them after unlocking the item?")
            unlock_msg = user_input
            escaped_prob = vr.sentenceSimilarity(unlock_msg, "You escaped.")
            print(escaped_prob)
            if escaped_prob > 0.7:
                print("{} is the escape item".format(item))
                update_query = '''UPDATE {} SET required_items = ? WHERE item="room"'''.format(room_name)
                cur.execute(update_query, (item,))

        update_query = '''UPDATE {} SET required_items =?, unlock_msg =?, unlock_action =? WHERE item=? '''.format(room_name)
        cur.execute(update_query, (required_item, unlock_msg, unlock_action, item))
        return pair

        
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







file = open("room_generator_log.txt","r+")
file.truncate(0)
file.close()

f = open("room_generator_log.txt", "a")
nlp = spacy.load('en_core_web_sm')


name_of_room = input("What do you want to call your room?").replace(" ", "_")
con, cur = createRoomDatabase(name_of_room)
print("DATABASE CREATED SUCCESSFULLY")


user_input = input("Tell me about the room:")


room_description = cur.execute('''INSERT INTO {} (item, description) VALUES ("room", ?)'''.format(name_of_room),(user_input,))



pairs_queue = deque((te.ContentExtractor(user_input)).items())
print(pairs_queue)

finished = False
while(not finished):
    if len(pairs_queue)>0:
        (o,(a,t)) = pairs_queue[0]

        description_of_item, pairs_queue = createItems(con, cur, name_of_room, o, a, pairs_queue)
    
        newpairs = (te.ContentExtractor(description_of_item)).items()
        pairs_queue.extendleft(newpairs)
        print(pairs_queue)
    else:
        user_input = input("Do you have anything else to add? ")


        if vr.sentenceSimilarity(user_input, "no") > 0.9:
            finished = True
        else:
            user_input = input("What else do you want to add? ")
            
            newpairs = te.ContentExtractor(vr.lemmatize(nlp,user_input)).items()
            pairs_queue.extendleft(newpairs)
            print(pairs_queue)


f.close()