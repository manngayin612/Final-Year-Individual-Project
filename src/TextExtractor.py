import VoiceRecognitionUtils as vr
import spacy 



def ContentExtractor(text):
    nlp = spacy.load("en_core_web_sm")

    # Coreference resolution
    # resolved = vr.coreferenceResolution(nlp, text)
    # print("Resolved text: ", resolved)

    
    # filtered = vr.stopWordRemoval(text)
    # print("Filtered: ", filtered)

    # print("Noun Extracted")
    # vr.identifyNoun(nlp, filtered)

    print("Verbs Extracted")
    vr.identifyVerb(nlp, text)









text = "There is a table in the room. There is a key on the table and it is used to unlock the door. The head of the ax is lying on the ground"

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