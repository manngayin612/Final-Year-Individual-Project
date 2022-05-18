import spacy 
import VoiceRecognitionUtils as vr
import sqlite3

def ContentExtractor(text):
    nlp = spacy.load("en_core_web_sm")
    pairs = {}
    
    if text != "":
        f = open("room_generator_log.txt", "a")
        f.write(text+".\n")
        f.close()
    
        with open("room_generator_log.txt", "r") as f:
            log = f.read()

        # Coreference resolution
        resolved_text = vr.coreferenceResolution(nlp, log, max_dist=1)
        
        # current_resolved_text = resolved_text.split("\n")[-2]
        current_resolved_text = text

        # for token in nlp(text):
        #     print(token, token.pos_, token.dep_)
        
        # text = vr.stopWordRemoval(text)
        # print("Filtered: ", text)

        doc = nlp(current_resolved_text)


        # for sent in doc.sents:
        print("Current: ",doc.text)
        # root = vr.getRoot(nlp, sent)
        direct_object = vr.identifySubject(nlp, doc.text.lower())

        print("Noun Extracted")
        print(set(direct_object), "\n")

        actions = vr.identifyVerb(nlp, doc.text.lower())
        
        print("Verbs Extracted")
        if len(actions) >0:
            print(set(actions), "\n")
        else:
            print("No action identified\n")

        tools = vr.identifyTools(nlp, doc.text.lower())
        print("Tools Extracted")
        print(tools, "\n")

        if len(direct_object) >0:
            pairs = vr.matchObjectWithAction(pairs, nlp, doc.text, direct_object, actions, tools) 

        print("\n")
    return pairs


# text = "There is a little box with a number lock on the wooden table in the middle of the room. The password of box is 1234. After unlocking the box, a key is inside to unlock the door."

# ContentExtractor(text)
