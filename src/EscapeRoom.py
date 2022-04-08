from py import process
import VoiceRecognitionUtils as vr 
# import nltk
# nltk.download('wordnet', force=True)
# nltk.download('omw-1.4', force=True)
# from nltk.corpus import wordnet as wn

voice_input = False
test = False


objects = ["table","door", "key"]
bag = []


# def createRoom(con):
#     print("Setting up the room....")
#     cur = con.cursor()

#     # Create table
#     cur.execute('''CREATE TABLE objects
#                (name text, colour text, qty real)''')
#     con.commit()

# def check_synonyms(word1, word2):
#     print(wn.synsets('pick_up', pos=wn.VERB))
#     word = wn.synsets('pick_up', pos=wn.VERB)[1]
#     for syn in wn.synsets(word1):
#         print(syn)
#         is_synonym = False
#         for lemma in syn.lemma_names():
#             if lemma == word2 and lemma != word1:
#                 is_synonym = True
#                 return True
#     return False

# # return a score denoting how similar two word senses are
# def check_similarity(word1, word2):
#     print(wn.synsets('pick_up', pos=wn.VERB)[1].definition())
#     word = wn.synsets('pick_up', pos=wn.VERB)[1]
#     for synsets in wn.synsets(word2, pos=wn.VERB):
#         print(word.definition())
#         print(synsets.definition(),synsets.path_similarity(word))

#     # word1_synset = wn.synset('collect.v.01')
#     # word2_synset = wn.synset('pick_up.v.02')
#     # print(word1_synset.path_similarity(word))

def processAction(action, subject, direct_object, indirect_object):
    if action == "pick up" or action in vr.getSynsetsList("pick_up"):
        if direct_object in objects:
            objects.remove(direct_object)
            bag.append(direct_object)
        else: 
            print("No such object")
    else:
        print("what do you want me to do?")
    print(objects)
    print(bag)
        






if __name__ == "__main__":

    # con = sqlite3.connect('EscapeRoom.db')
    # createRoom(con)
    if not test:
        print("Room Created!")

        if voice_input:
            input = vr.recogniseSpeech()
            print("Google Speech Recognition thinks you said \"" + input + "\"")
        else :
            input = input("Waiting for input... ")
            print("Input is \"" + input + "\"")

        action, subject, direct_object, indirect_object = vr.processSpeech(input)

        processAction(action, subject, direct_object, indirect_object)

        # if action == "pick up" or check_synonyms("pick up", action):
        #     if direct_object in objects:
        #         objects.remove(direct_object)
        #         bag.append(direct_object)
        #     else: 
        #         print("No such object")
        # else:
        #     print("what do you want me to do?")
        # print(objects)
        # print(bag)
    else:
        # check_similarity("pick up", "put_down")
        vr.getSynsetsList("collect")
        
    # con.close()
