DEFAULT_GAME_DIR = None # maybe use json
GAMES = []

class Game:
    def __init__(self):
        self.name = ""
        self.shortcut = ""
        self.icon = ""
        self.exec = ""
        self.wine_prefix = ""
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

class CustomPrefx:
    def __init__(self):
        self.name = ""
        self.path = ""
        self.dxvk_ver = ""

    def install_dxvk(self):
        print("preparing to download dxvk")
        # fetch version from somewhere
        self.dxvk_ver = "dxvk-1.10.1"
        if not os.path.isdir(".dxvk"):
            os.makedirs(".dxvk")
            os.chdir(self.PLANT_LAUNCHER_PATH + "/.dxvk")
            #I think it'd be smarter to fetch the dxvk version and then insert it here rather than manually setting it, or even better, leaving it to the user
            result = subprocess.Popen(["wget https://github.com/doitsujin/dxvk/releases/download/v" + self.dxvk_ver[5:len(self.dxvk_ver)] + "/" + self.dxvk_ver + ".tar.gz && tar -xvf " + self.dxvk_ver + ".tar.gz && rm -rvf" + self.dxvk_ver + ".tar.gz"], shell=True)
            result.wait()

    def install_vkd3d(self):
        print("preparing to download dxvk")
        self.vkd3d_ver = "vkd3d-proton-2.6"
        if not os.path.isdir(".vkd3d"):
            os.makedirs(".vkd3d")
            os.chdir(self.PLANT_LAUNCHER_PATH + "/.vkd3d")
            result = subprocess.Popen(["wget https://github.com/HansKristian-Work/vkd3d-proton/releases/download/v" + self.vkd3d_ver[13:len(self.vkd3d_ver)] + "/" + self.vkd3d_ver + ".tar.zst && tar --use-compress-program=unzstd -xvf " + self.vkd3d_ver + ".tar.zst && rm -rvf " + self.vkd3d_ver + ".tar.zst"], shell=True)
            result.wait()
        else:
            result = subprocess.Popen(["bash"])