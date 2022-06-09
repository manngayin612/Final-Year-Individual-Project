from json import tool
from tokenize import Token
import spacy
import neuralcoref
from spacy.matcher import Matcher
# import neuralcoref
import speech_recognition as sr
from sympy import hyper
from Input import Input
import ChatGenerator 
from random import randrange
import VoiceRecognitionUtils as vr
from sentence_transformers import SentenceTransformer, util
import pyttsx3
from gtts import gTTS


from nltk.corpus import wordnet as wn

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


def textToSpeech(text):

    engine = pyttsx3.init()
    engine.setProperty('voice', "com.apple.speech.synthesis.voice.daniel")
    engine.setProperty("rate", 160)

    engine.save_to_file(text, 'speech.mp3')
    print("saved to file")
    engine.runAndWait()
    print("run and wait")
    # engine.stop()

    # tts = gTTS(text)
    # tts.save('speech.wav')





def identifyActionsAndObjects(nlp, speech):
    # print("DETAILS OF SPEECH")
    # for token in speech:
    
    action = ""
    subject = ""
    direct_object = ""
    indirect_object = ""
    password = ""

    inputs = []
    temp = ()
    speech = nlp(speech)
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

def identifySubject(nlp, input):
    
    matcher = Matcher(nlp.vocab)

    pattern1 = [{"POS": "PROPN"} ]
    pattern2 = [{"POS": "NOUN"},{"POS": "NOUN", "OP":"?"}]
    pattern3 = [{"POS": "NOUN"}, {"LOWER": "of"},{"POS": "DET", "OP":"?"},{"POS":"NOUN"}]
    matcher.add("Noun", [pattern1, pattern2, pattern3])

    doc = nlp(input)
    matches = matcher(doc)

    noun_phrases = findLongestSpan(nlp, doc, matches)
    return noun_phrases



def identifyVerb(nlp, input):
    matcher = Matcher(nlp.vocab)

    pattern1 = [{"POS":"VERB"}, {"POS":"PART", "OP":"*"}, {"POS":"ADV", "OP":"*"}]
    pattern2 = [{"POS":"VERB"}, {"POS":"ADP", "OP":"*"}, 

                # {"POS": "DET", "OP":"*"},
                # {"POS": "AUX", "OP":"*"}, {"POS":"ADJ", "OP":"*"}, {"POS": "ADV", "OP":"*"}
                ]

    matcher.add("verb", [pattern1, pattern2])

    doc = nlp(input)

    matches = matcher(doc)
    
    if len(matches) > 0:
        verb_phrases = findLongestSpan(nlp, doc, matches)
        return [vr.lemmatize(nlp, v) for v in verb_phrases]
    else:
        return []

def identifyTools(nlp, input):
    matcher = Matcher(nlp.vocab)
    doc = nlp(input)
    
    pattern1 = [{"DEP":"pobj"}]

    matcher.add("tool", [pattern1])

    matches = matcher(doc)

    noun_phrases = findLongestSpan(nlp, doc, matches)
    return noun_phrases


def matchObjectWithAction(matches, nlp, sent, nouns, verbs, tools):
    doc = nlp(sent)
    temp_tools = []

    for token in doc:
        # print(token.text,token.dep_, token.head.head.lemma_)

        if str(token) in nouns:
            matches[token.lemma_] = ([],"")
            if token.head.lemma_.lower() in verbs:
                matches[token.lemma_][0].append(token.head.lemma_.lower())
            if token.dep_ == "pobj":
                temp_tools.append(token)

    for t in temp_tools:
        for (i, (a, _)) in matches.items():
            if t.head.head.lemma_.lower() in a:
                matches[i] = (a, t.lemma_)

    return matches



def getRoot(nlp, sent):
    # doc = nlp(sent)
    return sent.root

def getSpanText(doc, start, end):
    return str(doc[start:end])
        
def findLongestSpan(nlp, doc, matches):
    
    new_matches = []
    if len(matches) > 0:
        longest_span = matches[0]
        for match_id, start, end in matches:

            string_id = nlp.vocab.strings[match_id]
            if longest_span != None:
                (prev_id, prev_start, prev_end) = longest_span
                if prev_start  >= start+1 and prev_end <= end:
                    longest_span = (match_id, start, end) 
                elif prev_end  == start:
                    longest_span = (match_id, prev_start, end)
                elif start >= prev_start and start <= prev_end:
                    longest_span = (match_id, prev_start, end)
                else:
                    if getSpanText(doc, longest_span[1], longest_span[2]) not in new_matches:
                        # print("Add {} to new_matches".format(longest_span))
                        new_matches.append(getSpanText(doc, longest_span[1], longest_span[2]))
                    new_matches.append(getSpanText(doc, longest_span[1], longest_span[2]))
                    longest_span = (match_id, start, end)

        new_matches.append(getSpanText(doc, longest_span[1], longest_span[2]))

    return new_matches

def sentenceSimilarity(sent1, sent2):
    sentences = [sent1, sent2]
    model = SentenceTransformer('distilbert-base-nli-mean-tokens')
    # sentences = ['you escaped', 'where is the key', 'there is a key inside', 'bye', 'you are free now', 'there is a new room waiting for you']
    sentence_embeddings = model.encode(sentences)
    similarity = util.pytorch_cos_sim(sentence_embeddings[0], sentence_embeddings[1])
    print(similarity)
    return similarity


def stopWordRemoval(input):
    stopwords = ["a", "the", "an"]

    filtered = []
    for token in input.split():
        if token.lower() not in stopwords:
            filtered.append(token)

    return " ".join(str(x) for x in filtered)


def coreferenceResolution(nlp, input, max_dist = 500):
    coref = neuralcoref.NeuralCoref(nlp.vocab, max_dist= max_dist)
    nlp.add_pipe(coref, name='neuralcoref')
    doc = nlp(input)
    resolved = doc._.coref_resolved
    return resolved

def lemmatize(nlp, input):
    return " ".join([token.lemma_ for token in nlp(input)])


def processSpeech(input):
    nlp = spacy.load("en_core_web_sm")
    # Save current input to the log
    f = open("user_input_log.txt", "a")
    f.write(input+".\n")
    f.close()

    with open("user_input_log.txt", "r") as f:
        log = f.read()

    resolved = coreferenceResolution(nlp, log, max_dist=1)
    current_input = resolved.split("\n")[-2]

    print("Result from crefernceREsolution",current_input)


    inputs = identifyActionsAndObjects(nlp, current_input)
    print("Input result from identifyActionsAndObjects: ", inputs)
    # print("action: ",  action, " subject: ", subject, " direct object: ", direct_object, " indirect object: ", indirect_object, password )     

    # zipped = zip(action, direct_object, password)
    return inputs

def isSimilarWord(stored_word, input_word):
    synonyms = set([ss.name().split(".")[0] for ss in wn.synsets(stored_word, pos=wn.VERB)])
    hypernyms = set([h.name().split(".")[0]  for ss in wn.synsets(stored_word, pos=wn.VERB) for h in ss.hypernyms()])
    print(synonyms, hypernyms)
    return input_word in synonyms or input_word in hypernyms

    
def generateResponse(res):
    num_beams = 30
    num_return_sequences = 20
    responses = ChatGenerator.get_response(res,num_return_sequences,num_beams)
    index = randrange(len(responses))
    print(res, "--", responses[index])
    return responses[index]