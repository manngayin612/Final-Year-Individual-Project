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

    domain = ["furniture", "home"]

    token._.wordnet.wordnet_domains()

    in_domain = token._.wordnet.wordnet_synsets_for_domain(domain)

    if len(in_domain)>0:
        item_def = in_domain[0].name()

    else:  
        print("Searching for hypernym")
        for ss in wn.synsets(object, pos=wn.NOUN):
            print(ss.name())
            for s in ss.closure(lambda s:s.hypernyms()):
                print(s.lemma_names())
                if "physical_object" in s.lemma_names():
                    item_def = ss.name()
                    break
            else:
                continue
        
            break

    return object, item_def



def createItems(con, cur, object, action, queue):

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
        
    print(item_def, wn.synset(item_def).definition())

    unlock_msg = None
    required_item = None
    unlock_action = None

    combine_with = None
    finished_item = None

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

    stored_type = itemExisted(cur, item)
    print("Stored: ", stored_type)

    #item didnt existed at all
    description = ""
    if not stored_type:
        # Giving Description to the object
        description = input("Short description for {}: ".format(object))

        insert_object = """INSERT INTO room (type, item, item_def, action, description,required_items, unlock_msg, unlock_action,  combine_with, finished_item) VALUES (?,?,?,?,?,?,?,?,?,?)"""
        cur.execute(insert_object, (type, item, item_def, str(a), description, required_item, unlock_msg, unlock_action, combine_with, finished_item ))
    elif stored_type != type:
        print("Please update")
        update_record = """UPDATE room SET type = ? WHERE item = ?"""
        cur.execute(update_record, (type, item,))
    

    print("Check if all fields are completed.")
    isEntryCompleted(cur,item, type)
        
    
    print("\nCONFIRMING: inserted an {} object: {}\n".format(type, object))
    con.commit()
    queue.popleft()
    return description, queue
# else:
#     queue.popleft()
#     return "", queue


def isEntryCompleted(cur, item, type):
    if type == "unlock":
        get_record = """SELECT required_items, unlock_msg, unlock_action FROM room WHERE item=? and type = ?;"""
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

        
        if unlock_msg == None:
            user_input = input("What do you want to say to them after unlocking the item?")
            unlock_msg = user_input

        update_query = '''UPDATE room SET required_items =?, unlock_msg =?, unlock_action =?'''
        cur.execute(update_query, (required_item, unlock_msg, unlock_action,))

        
def itemExisted(cur, item_name):
    check_exist = """SELECT type FROM room WHERE item=?;"""
    result = cur.execute(check_exist, (item_name,))
    for row in result:
        return row[0]

def createRoomDatabase():
    con = sqlite3.connect("escaperoom.sqlite")
    cur = con.cursor()

    cur.execute('''DROP TABLE IF EXISTS room;''')
    cur.execute('''CREATE TABLE IF NOT EXISTS room(
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
        )''')

    return con, cur

con, cur = createRoomDatabase()

print("DATABASE CREATED SUCCESSFULLY")

nlp = spacy.load('en_core_web_sm')



user_input = input("Tell me about the room:")
# user_input=("The box is locked with the password 1234.")


for token in nlp(user_input):
    print(token, token.pos_, token.dep_)


pairs_queue = deque((te.ContentExtractor(user_input)).items())
print(pairs_queue)
finished = False
while(not finished):
    if len(pairs_queue)>0:
        (o,(a,t)) = pairs_queue[0]
        # print("Before creating Items:", pairs_queue)
        description_of_item, pairs_queue = createItems(con, cur, o, a, pairs_queue)
        # print("After creating items", pairs_queue)
        # f.write(description_of_item+".\n")
    
        newpairs = (te.ContentExtractor(description_of_item)).items()
        pairs_queue.extendleft(newpairs)
        # print("Appened pairs: ",pairs_queue)
    else:
        user_input = input("Do you have anything else to add? ")


        if user_input == "no":
            finished = True
        else:
            user_input = input("What else do you want to add? ")
            newpairs = te.ContentExtractor(vr.lemmatize(nlp,user_input)).items()
            pairs_queue.extendleft(newpairs)