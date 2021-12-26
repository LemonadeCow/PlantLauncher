import os, platform, subprocess, sys
import json
from pathlib import Path
import wx

#USE JSON TO STOR DEFAULT GAME DIR, AND THE GAME ARR

class Data:
    def __init__(self):
        self.DFAULT_GAME_DIR = "" # maybe use json
        self.GAMES = []    
data = Data()

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


class GameTab(wx.Panel):
    
    def __init__(self, parent, icon_size):
        super().__init__(parent)
        self.parent = parent

        icon = wx.Image(*icon_size)

        self.max_size = 75

        add_btn = wx.Button(self, label = 'Add Game')
        add_btn.Bind(wx.EVT_BUTTON, self.on_add)

        self.short_path = ""

        os.chdir(str(Path.home()) + "/PlantLauncher")

        for line in open(os.getcwd().replace("/Launcher", "") + "/Assets/games.json", "r"):
            if len(line.replace('\\n', '')) > 10:
                data.GAMES.append(json.loads(line))

        print(data.GAMES)

        self.g_b = []
        for i in range(len(data.GAMES)):
            self.g_b.append(0)

        print(data.GAMES)

        for i in range(len(data.GAMES)):
            img = wx.Image(data.GAMES[i]["icon"], wx.BITMAP_TYPE_ANY)

            W = img.GetWidth()
            H = img.GetHeight()

            new_w = self.max_size
            new_h = self.max_size * H / W
            
            img = img.Scale(new_w, new_h)

            bmp = wx.Bitmap(img)

            self.g_b[i] = wx.Button(self, id = 1, label = "", pos = (50,30), size = (new_w+10, new_h+10))
            self.g_b[i].SetBitmap(bmp)
            self.g_b[i].Bind(wx.EVT_BUTTON, lambda event : self.on_launch(event, data.GAMES[i]["id"]))
        
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.g_sizer = wx.GridSizer(6,5,5)

        self.hsizer.Add(add_btn, 0, wx.ALL, 5)
        self.g_sizer.AddMany(self.g_b)
        self.main_sizer.Add(self.hsizer)
        self.main_sizer.Add(self.g_sizer)
        self.SetSizer(self.main_sizer)
        self.main_sizer.Fit(self.parent)
        self.Layout()
    
    def on_add(self, event):
        """
        links the shortcut to the game
        """

        wildcard = "DESKTOP files (*.desktop)|*.desktop"
        with wx.FileDialog(None, "Choose a desktop file",
                          wildcard = wildcard,
                          style = wx.FD_OPEN) as dialog:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return

            pathname = dialog.GetPath()
            self.add_game(pathname) 

    def add_game(self, path):
        """
        adds properties to the game's index in the list and sets up the game in the gui
        """
        self.game = Game()
        self.game.shortcut = path
        desktop_file = open(self.game.shortcut, "r")

        self.game.icon = subprocess.Popen(['bash', 'PlantLauncher/.scripts/get_icon.sh' , self.game.shortcut], cwd=Path.home(), stdout=subprocess.PIPE)
        self.game.icon = str(self.game.icon.stdout.read())
        self.game.icon = self.game.icon.replace("b", "",1)
        self.game.icon = self.game.icon.replace("\\n", "",1)
        self.game.icon = self.game.icon.replace("\'", "")

        self.game.exec = subprocess.Popen(['bash', 'PlantLauncher/.scripts/get_executable.sh' , self.game.shortcut], cwd=Path.home(), stdout=subprocess.PIPE)
        self.game.exec = str(self.game.exec.stdout.readline())
        self.game.exec = self.game.exec.replace("b", "",1)
        self.game.exec = self.game.exec.replace("\\n", "",1)
        self.game.exec = self.game.exec.replace("\'", "")

        self.game.name = subprocess.Popen(['bash', 'PlantLauncher/.scripts/get_name.sh' , self.game.shortcut], cwd=Path.home(), stdout=subprocess.PIPE)
        self.game.name = str(self.game.name.stdout.readline())
        self.game.name = self.game.name.replace("b", "",1)
        self.game.name = self.game.name.replace("\\n", "",1)
        self.game.name = self.game.name.replace("\'", "")

        desktop_file.close()

        img = wx.Image(self.game.icon, wx.BITMAP_TYPE_ANY)

        W = img.GetWidth()
        H = img.GetHeight()

        new_w = self.max_size
        new_h = self.max_size * H / W
        
        img = img.Scale(new_w, new_h)

        bmp = wx.Bitmap(img)

        data.GAMES.append(self.game)
        self.game.id = data.GAMES.index(self.game)

        games_json = open(os.getcwd().replace("/Launcher", "") + "/Assets/games.json", "a")

        data.GAMES[self.game.id] = data.GAMES[self.game.id].to_json()
        tmp = json.dumps(data.GAMES[self.game.id])
        games_json.write("\n" + tmp)

        games_json.close()

        self.g_b.append(wx.Button(self, id = 1, label = "", size = (new_w+10, new_h+10), name=str(self.game.id)))
        self.g_b[len(self.g_b) - 1].SetBitmap(bmp)
        self.g_b[len(self.g_b) - 1].Bind(wx.EVT_BUTTON, lambda event : self.on_launch(event, self.game.id))

        self.main_sizer.Remove(self.g_sizer)
        print(data.GAMES)
        
        self.g_sizer = wx.GridSizer(5,0,0)
        self.g_sizer.AddMany(self.g_b)
        self.main_sizer.Add(self.g_sizer, wx.EXPAND | wx.ALL)
        self.Layout()
        self.Refresh()
        
    def on_launch(self, event, ind):
        """
        creates a tmp file and dir and creates the launch instructions for the game
        """
        if not os.path.isdir("/tmp/PlantLauncher"):
            os.makedirs("/tmp/PlantLauncher")
        f = open("/tmp/PlantLauncher/launch_instructions.sh", "a")
        f.write('#!bin/bash')
        f.write("\n" + data.GAMES[ind]["exec"])
        f.close()
        os.chdir(Path.home())
        os.system("bash /tmp/PlantLauncher/launch_instructions.sh")
        os.remove("/tmp/PlantLauncher/launch_instructions.sh")
        os.rmdir("/tmp/PlantLauncher")
        os.chdir(os.path.dirname(__file__))
        

class ConfigTab(wx.Panel):
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        title_dir = wx.StaticText(self,  label = "Default Folder")

        dir_b = wx.Button(self, label = "Set Default Game Folder")
        dir_b.Bind(wx.EVT_BUTTON, self.set_dir)

        font = wx.Font(16, family = wx.FONTFAMILY_MODERN, style = 0, weight = 100, 
                      underline = True, faceName ="", encoding = wx.FONTENCODING_DEFAULT)

        title_dir.SetFont(font)

        self.window_size = (500, 300)

        self.resized = False
        parent.Bind(wx.EVT_SIZE, self.OnSize)
        parent.Bind(wx.EVT_IDLE, self.OnIdle)
        self.g_titles =[]
        self.refresh_b = wx.Button(self, label = "Refresh", pos=(0 ,0))
        self.refresh_b.SetPosition((self.window_size[0] - self.refresh_b.GetSize()[0] - 5, 0))
        self.refresh_b.Bind(wx.EVT_BUTTON, self.show_games)
        
        self.dir_txt = wx.TextCtrl(self, size=(200, -1))

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        titledir_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.dir_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.g_sizer = wx.GridSizer(1, 20, 0)
        

        titledir_sizer.Add(title_dir, 0, wx.LEFT, 5)

        self.dir_sizer.Add(dir_b, 0, wx.ALL, 5)
        self.dir_sizer.Add(self.dir_txt, 0, wx.ALL, 5)
        
        self.main_sizer.Add(titledir_sizer, 0, wx.ALL, 5)
        self.main_sizer.Add(self.dir_sizer, 0, wx.ALL, 5)
        
        self.SetSizer(self.main_sizer)
        self.Layout()
        self.Refresh()

    def OnSize(self,event):
        self.resized = True # set dirty

    def OnIdle(self,event):
        if self.resized: 
            # take action if the dirty flag is set
            
            if self.GetSize()[0] >= 438 and self.GetSize()[1] >= 224:
                self.window_size = self.GetSize()
                self.refresh_b.SetPosition((self.window_size[0] - self.refresh_b.GetSize()[0], 0))
                self.resized = False # reset the flag

    def set_dir(self, event):
        with wx.DirDialog (None, "Choose input directory", "",
                    wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST) as dialog:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return # the user changed their mind

            data.DEFAULT_GAME_DIR = dialog.GetPath()
            self.dir_txt.SetValue(dialog.GetPath())
    
    def show_games(self, event):
        for i in range(len(self.g_titles)):
            self.g_titles[i].Destroy()
        print('what')
        self.g_titles = []
        for i in range(len(data.GAMES)):
            self.g_titles.append(0)
        
        font = wx.Font(12, family = wx.FONTFAMILY_MODERN, style = 0, weight = 100, 
                      underline = True)

        self.main_sizer.Remove(self.g_sizer)
        self.g_sizer = wx.GridSizer(1, 20, 1)
        for i in range(len(data.GAMES)):
            self.g_titles[i] = wx.StaticText(self, label=data.GAMES[i]["name"])
            self.g_titles[i].SetFont(font)
            self.g_sizer.Add(self.g_titles[i], 1, wx.EXPAND, 0)
            
        self.main_sizer.Add(self.g_sizer)

        self.SetSizer(self.main_sizer)
        self.Layout()
        self.Refresh()

frame_size = (0,0)

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title='Plant Launcher', size = (540, 300))

        panel = wx.Panel(self)
        nb = wx.Notebook(panel)
        game_tab = GameTab(nb, icon_size=(240,240))
        config_tab = ConfigTab(nb)

        nb.AddPage(game_tab, "games")
        nb.AddPage(config_tab, "config")
        
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        panel.SetSizer(sizer)
        self.Show(True)

if __name__ == '__main__':
    if "linux" in platform.system().lower():
        app = wx.App(redirect=False)
        frame = MainFrame()
        frame.SetMinSize(wx.Size(540, 300))
        app.MainLoop()
