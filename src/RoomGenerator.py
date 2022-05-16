import sqlite3
import TextExtractor as te
import spacy
from spacy_wordnet.wordnet_annotator import WordnetAnnotator 
from nltk.corpus import wordnet as wn
from Item import CombinableItem, Item, UnlockItem
from nltk.corpus import wordnet as wn
from collections import deque


# Normal items: name, item_def, actions, description
# Unlock items: name, unlock_msg, item_def, required_items, actions, unlock_action , description

def createItems(con, cur, object, action, queue):

    nlp = spacy.load('en_core_web_sm')
    nlp.add_pipe(WordnetAnnotator(nlp.lang), after='tagger')

    print("Item Existed? ", itemExisted(cur, object))

    if not itemExisted(cur, object):
        
        if  "room" in object:
            print("createItems: room ==> IGNORE")
            queue.popleft()
            return "", queue
        else:
            print("createItem ==> SEARCHING DOMAIN")
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

        print(item_def, wn.synset(item_def).definition())
        item = object


        # Giving Description to the object
        description = input("Short description for {}: ".format(object))

        unlock_msg = ""
        required_item = ""
        unlock_action = ""

        combine_with = ""
        finished_item = ""
        if "unlock" in action or "lock" in action:
            print("Creating Unlock Item")
            # item = UnlockItem(item, unlock_msg, item_def, required_items=required_item, action=action, description=description)
            #Store it into SQL

            type = "unlock"


            #TODO: Special case of a numberlock

        elif "combine" in action:
            print("Creating Combinable Item")
            # item = CombinableItem(self, name, item_def, combine_with, finished_item, actions=["get", "combine"], description="")
            # Store to SQL
            type = "combine"


        else:
            print("Creating Normal Item")
            # item = Item(item, item_def, description = description)
            # Store to SQL
            type = "normal"

        insert_object = """INSERT INTO room (type, item, item_def, action, description,required_items, unlock_msg, unlock_action,  combine_with, finished_item) VALUES (?,?,?,?,?,?,?,?,?,?)"""
        cur.execute(insert_object, ("combine", item, item_def, str(a), description, required_item, unlock_msg, unlock_action, combine_with, finished_item ))

        print("\nCONFIRMING: inserted an {} object: {}\n".format(type, object))
        con.commit()
        queue.popleft()
        return description, queue
    else:
        queue.popleft()
        return "", queue


def itemExisted(cur, item_name):
    check_exist = """SELECT EXISTS(SELECT 1 FROM room WHERE item=?);"""
    result = cur.execute(check_exist, (item_name,))
    return result.fetchone()[0]

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
    print(token, token.pos_)
pairs_queue = deque(te.ContentExtractor(user_input).items())
finished = False
while(not finished):
    if len(pairs_queue)>0:
        (o,a) = pairs_queue[0]
        print("Before creating Items:", pairs_queue)
        description_of_item, pairs_queue = createItems(con, cur, o, a, pairs_queue)
        print("After creating items", pairs_queue)
        newpairs = (te.ContentExtractor(description_of_item)).items()
        pairs_queue.extendleft(newpairs)
        print("Appened pairs: ",pairs_queue)
    else:
        user_input = input("Do you have anything else to add? ")

        if user_input == "no":
            finished = True
        else:
            user_input = input("What else do you want to add? ")
            newpairs = te.ContentExtractor(user_input).items()
            pairs_queue.extendleft(newpairs)