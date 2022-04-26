import spacy
class Input:
    def __init__(self, action, item, tool="", password=""):
        # self.raw_input = raw_input

        self.action = action
        self.item = item
        self.tool = tool
        self.password = password
