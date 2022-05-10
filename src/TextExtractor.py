import spacy 
import VoiceRecognitionUtils as vr
import sqlite3

con = sqlite3.connect("escaperoom.db")


    


def ContentExtractor(text):
    nlp = spacy.load("en_core_web_sm")

    # Coreference resolution
    text = vr.coreferenceResolution(nlp, text)
    print("Resolved text: ", text)

    
    # text = vr.stopWordRemoval(text)
    # print("Filtered: ", text)

    doc = nlp(text)

    pairs = {}


    for sent in doc.sents:
        print("Current: ",sent.text)
        root = vr.getRoot(nlp, sent)
        objects = vr.identifyNoun(nlp, sent.text)
        # print("Noun Extracted")
        # print(set(objects))

        actions = vr.identifyVerb(nlp, sent.text)
        # print("Verbs Extracted")
        # if len(actions) >0:
        #     print(set(actions))
        # else:
        #     print("No action identified")

        pairs = vr.matchObjectWithAction(pairs, nlp, sent.text, objects, actions)

        # for token in sent:
        #     if token.text in objects and token.head == root:
        #         print(token.text, token.dep_, token.head.text)
        print("\n")
    return pairs


# text = "There is a little box with a number lock on the wooden table in the middle of the room. The password of box is 1234. After unlocking the box, a key is inside to unlock the door."

# ContentExtractor(text)
