import VoiceRecognitionUtils as vr



def ContentExtractor(text):
    print("Noun Extracted")

    vr.IdentifyNoun(text)



text = "There is a table in the room. There is a key on the table and it is used to unlock the door."
ContentExtractor(text)
