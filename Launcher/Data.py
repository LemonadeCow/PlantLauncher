DEFAULT_GAME_DIR = None # maybe use json
GAMES = []

class Game:
    def __init__(self):
        self.name = ""
        self.shortcut = ""
        self.icon = ""
        self.exec = ""
        self.id = -1
    
    def to_json(self):
        tmp = {
            "name" : self.name,
            "shortcut" : self.shortcut,
            "icon" : self.icon,
            "exec" : self.exec,
            "id" : self.id
        }
        return tmp