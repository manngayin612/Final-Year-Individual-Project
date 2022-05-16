from tokenize import Token
import spacy
import neuralcoref
from spacy.matcher import Matcher
# import neuralcoref
import speech_recognition as sr
from Input import Input
import ChatGenerator 
from random import randrange
from spacytextblob.spacytextblob import SpacyTextBlob

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

def identifyNoun(nlp, input):
    
    matcher = Matcher(nlp.vocab)
    # Add match ID "HelloWorld
    # " with no callback and one pattern
    pattern1 = [{"POS": "PROPN"} ]
    pattern2 = [{"POS": "NOUN"},{"POS": "NOUN", "OP":"?"}]
    pattern3 = [{"POS": "NOUN"}, {"LOWER": "of"},{"POS": "DET", "OP":"?"},{"POS":"NOUN"}]
    matcher.add("Noun", [pattern1, pattern2, pattern3])

    doc = nlp(input)
    print("in identify noun", doc)
    matches = matcher(doc)
    print(matches)

    noun_phrases = findLongestSpan(nlp, doc, matches)
    return noun_phrases



def identifyVerb(nlp, input):
    matcher = Matcher(nlp.vocab)

    #define the pattern 


    pattern1 = [{"POS":"VERB"}, {"POS":"PART", "OP":"*"}, {"POS":"ADV", "OP":"*"}]

    pattern2 = [{"POS":"VERB"}, {"POS":"ADP", "OP":"*"}, 
    
                # {"POS": "DET", "OP":"*"},
                # {"POS": "AUX", "OP":"*"}, {"POS":"ADJ", "OP":"*"}, {"POS": "ADV", "OP":"*"}
                ]

    matcher.add("verb", [pattern1, pattern2])

    doc = nlp(input)

    matches = matcher(doc)
    print(matches)
    
    if len(matches) > 0:
        verb_phrases = findLongestSpan(nlp, doc, matches)
        return verb_phrases
    else:
        return []

def matchObjectWithAction(matches, nlp, sent, nouns, verbs):
    doc = nlp(sent)

    for token in doc:

        if str(token) in nouns:
            # if str(n).lower() == token.lemma_:
            matches[token.lemma_] = []
            print("matching action ", token.lemma_, token.head.lemma_)
            if token.head.lemma_.lower() in verbs:
                matches[token.lemma_].append(token.head.lemma_.lower())
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
            # print("\n")
            string_id = nlp.vocab.strings[match_id]
            # print(match_id, string_id, start, end ,getSpanText(doc, start, end))
            if longest_span != None:
                (prev_id, prev_start, prev_end) = longest_span
                #Merge case: one span is within another span e.g. "is writing a blog" "a blog"
                if prev_start  >= start+1 and prev_end <= end:
                    # print("DELETED {} {} {}".format( prev_start, prev_end , getSpanText(doc, prev_start, prev_end)))
                    longest_span = (match_id, start, end) 
                elif prev_end  == start:
                    # print("ADDED {} {} {}".format(prev_start, end ,getSpanText(doc, prev_start, end)))
                    # print("DELETED {} {} {}".format(prev_start, prev_end ,getSpanText(doc, prev_start, prev_end)))
                    # print("DELETED {} {} {}".format(start, end ,getSpanText(doc, start, end)))
                    longest_span = (match_id, prev_start, end)
                elif start >= prev_start and start <= prev_end:
                    longest_span = (match_id, prev_start, end)
                    # print("ADDED {} {} {}".format(prev_start, end, getSpanText(doc, prev_start, end)))
                    # print("DELETED {} {} {}".format(prev_start, prev_end, getSpanText(doc, prev_start, prev_end)))
                    # print("DELETED {}{}{}".format(start, end, getSpanText(doc, start, end)))
                else:
                    if getSpanText(doc, longest_span[1], longest_span[2]) not in new_matches:
                        # print("Add {} to new_matches".format(longest_span))
                        new_matches.append(getSpanText(doc, longest_span[1], longest_span[2]))
                    new_matches.append(getSpanText(doc, longest_span[1], longest_span[2]))
                    longest_span = (match_id, start, end)

            # print("TEMP:", longest_span)

        new_matches.append(getSpanText(doc, longest_span[1], longest_span[2]))
    

        # print("\nFinal Matches")
        # for (_, start, end) in new_matches:
        #     print(start, end, getSpanText(doc, start,end))

    return new_matches


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