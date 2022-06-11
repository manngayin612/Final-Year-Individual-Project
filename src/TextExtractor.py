import spacy 
import VoiceRecognitionUtils as vr
import time
debug = False
eval = True

def ContentExtractor(text):
    nlp = spacy.load("en_core_web_sm")
    pairs = {}
    
    if text != "":
        if eval: start_time = time.process_time()
        f = open("room_generator_log.txt", "a")
        f.write(text+".\n")
        f.close()
    
        with open("room_generator_log.txt", "r") as f:
            log = f.read()

        # Coreference resolution
        resolved_text = vr.coreferenceResolution(nlp, log, max_dist=1)

        # if debug: print("Current: ", resolved_text.split("\n"))    
        current_resolved_text = resolved_text.split("\n")[-2]
        if eval: print("Coreference Resolution: ", time.process_time() - start_time)

        doc = nlp(current_resolved_text)
        if debug: print("Current: ",doc.text)
        
        if eval: start_time = time.process_time()
        direct_object = vr.identifySubject(nlp, doc.text.lower())
        if eval: print("Identify Subject ", time.process_time() - start_time)

        if debug: print("Noun Extracted")
        if debug: print(set(direct_object), "\n")

        if eval: start_time = time.process_time()
        actions = vr.identifyVerb(nlp, doc.text.lower())
        if eval: print("Identify Verb: ", time.process_time() - start_time)
        
        if debug: print("Verbs Extracted")
        if len(actions) >0:
            if debug: print(set(actions), "\n")
        else:
            if debug: print("No action identified\n")

        if eval: start_time = time.process_time()
        tools = vr.identifyTools(nlp, doc.text.lower())
        if eval: print("Identify Tools: ", time.process_time() - start_time)
        if debug: print("Tools Extracted")
        if debug: print(tools, "\n")


        if len(direct_object) >0:
            if eval: start_time = time.process_time()
            pairs = vr.matchObjectWithAction(pairs, nlp, doc.text, direct_object, actions, tools) 
            if eval: print("Match object with action: ", time.process_time() - start_time)

        if debug: print("\n")
    return pairs


# text = "There is a little box with a number lock on the wooden table in the middle of the room. The password of box is 1234. After unlocking the box, a key is inside to unlock the door."

# ContentExtractor(text)
