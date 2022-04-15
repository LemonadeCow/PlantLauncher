DEFAULT_GAME_DIR = None # maybe use json
GAMES = []

class Game:
    def __init__(self):
        self.name = ""
        self.shortcut = ""
        self.icon = ""
        self.exec = ""
        self.id = -1
        self.epic_id = ""
    
    def to_json(self):
        tmp = {
            "name" : self.name,
            "shortcut" : self.shortcut,
            "icon" : self.icon,
            "exec" : self.exec,
            "epic_id" : self.epic_id,
            "id" : self.id
        }
        return tmp

class Folder:
    def __init__(self):
        self.name = ""
        self.games = []

    def to_json(self):
        tmp = {
            "name" : self.name,
            "games" : self.games
        }
        return tmp