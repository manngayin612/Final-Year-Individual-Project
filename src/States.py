import enum
class States(enum.Enum):
    UPDATE_STORED_ITEM = 1


class StatesDict(dict):

    def __init__(self):
      self._dict = {}