import sqlite3
import TextExtractor as te
import spacy
from spacy_wordnet.wordnet_annotator import WordnetAnnotator 
from nltk.corpus import wordnet as wn
from Item import CombinableItem, Item, UnlockItem


# Normal items: name, item_def, actions, description
# Unlock items: name, unlock_msg, item_def, required_items, actions, unlock_action , description

def createItems(con, cur, object, action):

    nlp = spacy.load('en_core_web_sm')
    nlp.add_pipe(WordnetAnnotator(nlp.lang), after='tagger')

    if object == "key":
        item_def = "key.n.01"
    elif "room" in object:
        pass
    else:
        token = nlp(object)[0]

        domain = ["furniture"]
        # synsets = token._.wordnet.wordnet_synsets_for_domain(domain)        
        token._.wordnet.wordnet_domains()
        # Choosing definition for the object
        # in_domain = []
        # for ss in token._.wordnet.synsets():
        #     lemma_name = nlp(ss.name().split(".")[0])[0]
        in_domain = token._.wordnet.wordnet_synsets_for_domain(domain)
        # print("in_domain: ",in_domain)

            # if lemma_name.text == object and ss in in_domain:
            #     print(ss.name(), ss.definition())
            #     list_of_def.append((ss.name(), ss.definition()))

        # For now just randomly choose one coz it doesn't matter
        item_def = in_domain[0].name()
    print(item_def, wn.synset(item_def).definition())
    item = object


    # Actions for this object
    

    # Giving Description to the object
    description = input("Short description for {}: ".format(object))
    # TODO: deal with other objects mentioned in description

    unlock_msg = ""
    required_item = ""

    combine_with = ""
    finished_item = ""
    if "unlock" in action:
        print("Creating Unlock Item")
        # item = UnlockItem(item, unlock_msg, item_def, required_items=required_item, action=action, description=description)
        #Store it into SQL
        insert_object = """INSERT INTO room (type, item, item_def, action, description, required_items, unlock_msg) VALUES (?,?,?,?,?,?,?) """
        cur.execute(insert_object, ("unlock", item, item_def, str(a), description, required_item, unlock_msg))
        con.commit()

        #TODO: Special case of a numberlock

    elif "combine" in action:
        print("Creating Combinable Item")
        # item = CombinableItem(self, name, item_def, combine_with, finished_item, actions=["get", "combine"], description="")
        # Store to SQL
        insert_object = """INSERT INTO room (type, item, item_def, action, description, combine_with, finished_item) VALUES (?,?,?,?,?,?,?)"""
        cur.execute(insert_object, ("combine", item, item_def, str(a), description, combine_with, finished_item ))
        con.commit()

    else:
        print("Creating Normal Item")
        # item = Item(item, item_def, description = description)
        # Store to SQL

        insert_object = """INSERT INTO room
                (type, item, item_def,  action, description) 
                VALUES 
                (?,?,?,?,?)"""
        cur.execute(insert_object, ("normal",item, item_def, str(a), description ))
        con.commit()

    return description
        


        # print("Choose the definition for the object: ")
        # number = list(range(len(list_of_def)))
        # zipped_list_of_def = zip(number, list_of_def)
        # for (i, (n, d)) in zipped_list_of_def:
        #     print(i, d)
        
        # choice = input()
        # item_def = list_of_def[int(choice)][0]
        # print(item_def)

        # Checking actions:


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
        unlock_action text)''')

    return con, cur


# def createRoomDatabase():

#     con = sqlite3.connect('escaperoom.sqlite')

#     cur = con.cursor()

#     cur.execute('''DROP TABLE IF EXISTS room;''')
#     cur.execute('''CREATE TABLE IF NOT EXISTS room (
#                     object text, type text, action text, description text)''')

#     # user_input= input("Please tell me how does the room look like in overall: ")

#     pairs = te.ContentExtractor("There is a little table in the middle of the room") 


#     while len(pairs) > 0 :
#         for (o,a) in pairs.items():
#             check_exist = """SELECT EXISTS(SELECT 1 FROM room WHERE object=?);"""
#             result = cur.execute(check_exist, (o,))
#             if not result.fetchone()[0]: 
#                 description = input("Short description for {}: ".format(o))
#                 print(o, description)

#                 pairs = te.ContentExtractor(description)

#             # if not cur.execute(check_exist, (o,)):

#                 insert_object = """INSERT INTO room
#                             (object, type, action, description) 
#                             VALUES 
#                             (?,?,?,?)"""
#                 cur.execute(insert_object, (o, "combinable",str(a), description ))
#                 con.commit()

#                 select_all = """SELECT * FROM room"""
#                 result = cur.execute(select_all)
#                 print(result.fetchall())
#                 print(pairs)


# createRoomDatabase()

# # con.commit()

# # con.close()
con, cur = createRoomDatabase()

print("DATABASE CREATED SUCCESSFULLY")

nlp = spacy.load('en_core_web_sm')
user_input = input("Tell me about the room:")
# user_input=("The box is locked with the password 1234.")


for token in nlp(user_input):
    print(token, token.pos_)
pairs = te.ContentExtractor(user_input)
print(pairs)
finished = False
while(not finished):
    for (o, a) in pairs.items(): 
        user_input = createItems(con, cur, o, a)
        pairs = te.ContentExtractor(user_input)
    
    if len(pairs) == 0 :
        user_input = input("Do you have anything else to add?")
        if user_input == "no":
            finished = True
