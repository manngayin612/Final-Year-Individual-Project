import spacy 
import VoiceRecognitionUtils as vr
debug = False


def ContentExtractor(text):
    nlp = spacy.load("en_core_web_sm")
    pairs = {}
    
    if text != "":
        text = text +"."
        f = open("room_generator_log.txt", "a")
        f.write(text+".\n")
        f.close()
    
        with open("room_generator_log.txt", "r") as f:
            log = f.read()

        # Coreference resolution
        resolved_text = vr.coreferenceResolution(nlp, log, max_dist=1)
        current_resolved_text = resolved_text.split("\n")[-2]
        doc = nlp(current_resolved_text)
        if debug: print("Current: ",doc.text)
        

        direct_object = vr.identifySubject(nlp, doc.text.lower())

        actions = vr.identifyVerb(nlp, doc.text.lower())

    
        if debug: print("Verbs Extracted")
        if len(actions) >0:
            if debug: print(set(actions), "\n")
        else:
            if debug: print("No action identified\n")


        tools = vr.identifyTools(nlp, doc.text.lower())
        if debug: print("Tools Extracted")
        if debug: print(tools, "\n")


        if len(direct_object) >0:
            pairs = vr.matchObjectWithAction(pairs, nlp, doc.text, direct_object, actions, tools) 

    return pairs


# text = "There is a little box with a number lock on the wooden table in the middle of the room. The password of box is 1234. After unlocking the box, a key is inside to unlock the door."

# ContentExtractor(text)
