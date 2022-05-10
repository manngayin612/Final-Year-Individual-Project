import sqlite3
import TextExtractor as te
from nltk.corpus import wordnet as wn



# Normal items: name, item_def, actions, action_def, description
def createItems(object, action, type):
        # Giving Description to the object
        description = input("Short description for {}: ".format(object))

        # deal with other objects mentioned in description

        # Choosing definition for the object
        list_of_def = []
        for ss in wn.synsets(object,pos=wn.NOUN):
            lemma_name = ss.name().split(".")[0]
            if lemma_name == object:
                list_of_def.append((ss.name(), ss.definition()))

        print("Choose the definition for the object: ")
        number = list(range(len(list_of_def)))
        zipped_list_of_def = zip(number, list_of_def)
        for (i, (n, d)) in zipped_list_of_def:
            print(i, d)
        
        choice = input()
        item_def = list_of_def[int(choice)][0]
        print(item_def)




    
# Unlock items: name, unlock_msg, item_def, required_items, actions, action_def, unlock_action , description

    


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
user_input = ("There is a little table in the middle of the room")

pairs = te.ContentExtractor(user_input)
for (o, a) in pairs.items(): 
    type = "normal"
    createItems(o, a, type)