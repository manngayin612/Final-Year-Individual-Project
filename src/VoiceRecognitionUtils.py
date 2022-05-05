from tokenize import Token
import spacy
from spacy.matcher import Matcher
# import neuralcoref
import speech_recognition as sr
from Input import Input
import ChatGenerator 
from random import randrange

# from spacy import displacy

from spacy_wordnet.wordnet_annotator import WordnetAnnotator 


def recogniseSpeech():

    r = sr.Recognizer()

    # Get audio from microphone
    with sr.Microphone() as source:
        print("Recording voice...")
        audio = r.listen(source,timeout=8,phrase_time_limit=8)

    # Recognise Speech by Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        speech = r.recognize_google(audio)
        print("Result of Google Speech Recognition: {}".format(speech))
        return speech
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Googlse Speech Recognition service; {0}".format(e))




def identifyActionsAndObjects(speech):
    # print("DETAILS OF SPEECH")
    # for token in speech:
    
    action = ""
    subject = ""
    direct_object = ""
    indirect_object = ""
    password = ""

    inputs = []
    temp = ()
    for token in speech:
        print(token.text, token.pos_, token.dep_, token.head.text)
        # print(action, direct_object, indirect_object)
        if(token.pos_ == 'VERB'):
            # action.append(token.text)
            action = token.text
        elif(token.pos_ == 'NOUN'):
            if(token.dep_ == 'dobj'):
                direct_object = token.text
            elif(token.dep_ == "pobj"):
                if token.head.text == "of":
                    if temp[1] == "pobj":
                        indirect_object = token.text + "_" +  temp[0]
                    else :
                        direct_object = token.text + "_" + temp[0]
                elif token.head.pos_ != "ADP":
                    direct_object = token.text
                else:
                    indirect_object = token.text
        elif(token.pos_ == "NUM"):
            password = token.text 
        elif(token.pos_ == "CCONJ"):
            inputs.append(Input(action, direct_object, tool=indirect_object,password=password))
            action = ""
            subject = ""
            direct_object = ""
            indirect_object = ""
            password = ""
        elif(token.pos_ == "ADP"):
            if token.text == "of":
                temp = (token.head.text, token.head.dep_)
        else:
            continue
    print("action: ", action,"direct object: ", direct_object, "tool: ",indirect_object)
    
        
    inputs.append(Input(action, direct_object, tool=indirect_object, password=password))
    

    return inputs

def IdentifyNoun(input):
    nlp = spacy.load("en_core_web_sm")
    matcher = Matcher(nlp.vocab)
    # Add match ID "HelloWorld
    # " with no callback and one pattern
    pattern_1 = [{"POS":"ADJ", "OP" : "?"}, {"POS": "NOUN", "OP": "+"}]
    pattern_2 = [{"POS": "NOUN"}, {"LOWER": "of"}, {"POS": "NOUN"}]
    matcher.add("Noun", [pattern_1, pattern_2])

    doc = nlp(input)
    matches = matcher(doc)

    for match_id, start, end in matches:
        string_id = nlp.vocab.strings[match_id]  # Get string representation
        span = doc[start:end]  # The matched span
        print(match_id, string_id, start, end, span.text)



def stopWordRemoval(input):
    stopwords = ["a", "the", "an"]

    filtered = []
    for token in input.split():
        if token.lower() not in stopwords:
            filtered.append(token)

    return " ".join(str(x) for x in filtered)


# def coreferenceResolution(input, max_dist = 500):
        
#     en_nlp = spacy.load('en_core_web_sm')
#     # print(en_nlp.pipe_names)
#     coref = neuralcoref.NeuralCoref(en_nlp.vocab, max_dist=max_dist)
#     en_nlp.add_pipe(coref, name='neuralcoref')

#     # with open("user_input_log.txt", "r") as f:
#     #     doc = en_nlp(f.read())
#     doc = en_nlp(input)

#     # current_input  = en_nlp(input)
#     resolved = doc._.coref_resolved

#     # with open("user_input_log.txt", "w") as f:
#     #     f.write(resolved)    
#     return resolved
#     # current_input = en_nlp(resolved.split("\n")[-2])
#     # print(resolved.split("\n"))


#     # return current_input



def processSpeech(input):
    # Save current input to the log
    f = open("user_input_log.txt", "a")
    f.write(input+".\n")
    f.close()

    with open("user_input_log.txt", "r") as f:
        log = f.read()

    resolved = coreferenceResolution(log, max_dist=1)
    current_input = resolved.split("\n")[-2]

    print("Result from crefernceREsolution",current_input)


    inputs = identifyActionsAndObjects(current_input)
    print("Input result from identifyActionsAndObjects: ", inputs)
    # print("action: ",  action, " subject: ", subject, " direct object: ", direct_object, " indirect object: ", indirect_object, password )     

    # zipped = zip(action, direct_object, password)
 

    return inputs

    
# def getSynsetsList(word):
#     nlp = spacy.load('en_core_web_sm')
#     nlp.add_pipe("spacy_wordnet", after='tagger', config={'lang': nlp.lang})
#     token = nlp(word)[0]

#     synsets = token._.wordnet.synsets()
#     # print(word)
#     # for ss in synsets:
#     #     for hyper in ss.hypernyms():
#     #         print(ss,hyper)
#     lemmas_for_synsets = [lemma for s in synsets for lemma in s.lemma_names()]
#     hypernyms = [hyper for s in synsets for hyper_synset in s.hypernyms() for hyper in hyper_synset.lemma_names()]
#     # TODO: Filter the ones with low similarity
#     return set(lemmas_for_synsets+hypernyms)


def generateResponse(res):
    num_beams = 30
    num_return_sequences = 20
    responses = ChatGenerator.get_response(res,num_return_sequences,num_beams)
    index = randrange(len(responses))
    print(res, "--", responses[index])
    return responses[index]