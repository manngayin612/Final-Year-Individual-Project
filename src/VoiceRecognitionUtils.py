from tokenize import Token
import spacy
import speech_recognition as sr
from spacy import displacy

from spacy_wordnet.wordnet_annotator import WordnetAnnotator 


# from spacy.tokenizer import Tokenizer 
# from spacy.lang.en import English


def recogniseSpeech():

    r = sr.Recognizer()

    # Get audio from microphone
    with sr.Microphone() as source:
        print("Recording voice...")
        audio = r.listen(source)

    # Recognise Speech by Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        speech = r.recognize_google(audio)
        return speech
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Googlse Speech Recognition service; {0}".format(e))




def identifyActionsAndObjects(speech):
    print("DETAILS OF SPEECH")
    for token in speech:
        print(token.text, token.pos_, token.dep_, token.head.text)
    
    action = ""
    subject = ""
    direct_object = ""
    indirect_object = ""

    for token in speech:
        if(token.pos_ == 'VERB'):
            action = token.text
        elif(token.dep_ == 'dobj'):
            direct_object = token.text 
        elif(token.dep_ == 'pobj'):
            subject = token.text 
        elif(token.dep_ == 'dative'):
            indirect_object = token.text
        elif(token.head.text == action and token.pos_ == "ADP" ):
            action += " " + token.text

    print("------------SUMMARY-------------")
    return action, subject, direct_object, indirect_object



def processSpeech(input):
    en_nlp = spacy.load('en_core_web_sm')
    speech =  en_nlp(input)

    for label in en_nlp.get_pipe("parser").labels:
        print(label, " -- ", spacy.explain(label))
        

    print("--------------------------------------")

    (action, subject, direct_object, indirect_object) = identifyActionsAndObjects(speech)
    print("action: ",  action, " subject: ", subject, " direct object: ", direct_object, " indirect object: ", indirect_object )     
    return action, subject, direct_object, indirect_object

    
def getSynsetsList(word):
    nlp = spacy.load('en_core_web_sm')
    nlp.add_pipe("spacy_wordnet", after='tagger', config={'lang': nlp.lang})
    token = nlp(word)[0]

    synsets = token._.wordnet.synsets()
    lemmas_for_synsets = [lemma for s in synsets for lemma in s.lemma_names()]
    return set(lemmas_for_synsets)






# if __name__ == "__main__":

#     if voice_input:
#         input = recogniseSpeech()
#         print("Google Speech Recognition thinks you said \"" + input + "\"")
#     else :
#         input = input("Waiting for input... ")
#         print("Input is \"" + input + "\"")

    


    


    



    # Test similarity


    