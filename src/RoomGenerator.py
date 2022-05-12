import sqlite3
import TextExtractor as te
import spacy
from spacy_wordnet.wordnet_annotator import WordnetAnnotator 
from nltk.corpus import wordnet as wn
from Item import Item, UnlockItem


# Normal items: name, item_def, actions, action_def, description
# Unlock items: name, unlock_msg, item_def, required_items, actions, action_def, unlock_action , description

def createItems(object, action):

    nlp = spacy.load('en_core_web_sm')
    nlp.add_pipe(WordnetAnnotator(nlp.lang), after='tagger')

    if object == "key":
        item_def = "key.n.01"
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

    if action == "unlock":
        type = "unlcok_item"
    elif action == "combine":
        type = "combinable_item"
    else:
        type = "normal_item"
        item = Item(item, item_def, description = description)

    



    




        # print("Choose the definition for the object: ")
        # number = list(range(len(list_of_def)))
        # zipped_list_of_def = zip(number, list_of_def)
        # for (i, (n, d)) in zipped_list_of_def:
        #     print(i, d)
        
        # choice = input()
        # item_def = list_of_def[int(choice)][0]
        # print(item_def)

        # Checking actions:







    


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
nlp = spacy.load('en_core_web_sm')
user_input = ("Unlock the box to get the key.")

pairs = te.ContentExtractor(user_input)
print(pairs)
for (o, a) in pairs.items(): 

    createItems(o, a)


