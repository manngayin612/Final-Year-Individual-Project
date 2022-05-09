import spacy 
import VoiceRecognitionUtils as vr



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
        print(sent.text)
        print("Noun Extracted")
        objects = vr.identifyNoun(nlp, sent.text)
        print(set(objects))

        print("Verbs Extracted")
        actions = vr.identifyVerb(nlp, sent.text)
        if len(actions) >0:
            print(set(actions))
        else:
            print("No action identified")

        print("\n")
        pairs = vr.matchObjectWithAction(pairs, nlp, sent.text, objects, actions)

    print(pairs)




text = "There is a wooden table in the middle of the room. On the table, there is a little box with a number lock. The password of the number lock is 1234. After unlocking the box, a key is inside to unlock the door."

ContentExtractor(text)

# import spacy
# from spacy.matcher import Matcher
# nlp = spacy.load("en_core_web_sm")
# matcher = Matcher(nlp.vocab)
# # Add match ID "HelloWorld
# # " with no callback and one pattern
# pattern_1 = [{"POS":"ADJ", "OP" : "?"}, {"POS": "NOUN", "OP": "+"}]
# pattern_2 = [{"POS": "NOUN"}, {"LOWER": "of"}, {"POS": "NOUN"}]
# matcher.add("Noun", [pattern_1, pattern_2])

# doc = nlp("There is a table in the room. There is a key on the table and it is used to unlock the door. The door bell is lying on the ground. There is also a head of ax")
# matches = matcher(doc)
# for match_id, start, end in matches:
#     string_id = nlp.vocab.strings[match_id]  # Get string representation
#     span = doc[start:end]  # The matched span
#     print(match_id, string_id, start, end, span.text)