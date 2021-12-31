import os, platform, subprocess, sys
from os.path import exists
import json
from pathlib import Path
import wx, wx.svg, wx.lib.scrolledpanel as scrolled
import Data


class GameTab(scrolled.ScrolledPanel):
    
    def __init__(self, parent, icon_size):
        super().__init__(parent)
        self.parent = parent

        scrolled.ScrolledPanel.__init__(self, parent, -1)

        icon = wx.Image(*icon_size)

        self.max_size = 75

        add_btn = wx.Button(self, label = 'Add Game')
        add_btn.Bind(wx.EVT_BUTTON, self.on_add)

        self.edit = False
        self.e_b = []
        self.edit_btn = wx.Button(self, label='Edit')
        self.edit_btn.Bind(wx.EVT_BUTTON, self.on_edit)
        self.edit_btn.SetPosition((add_btn.GetPosition()[0] + self.edit_btn.GetSize()[0] + 20, 5))

        self.short_path = ""

        os.chdir(str(Path.home()) + "/PlantLauncher")

        if exists("Assets/games.json"):
            for line in open("Assets/games.json", "r"):
                if len(line.replace('\\n', '')) > 10:
                    Data.GAMES.append(json.loads(line))
        else:
            tmp = open("Assets/games.json", 'w')
            tmp.write('')
            tmp.close()

        self.g_b = []
        for i in range(len(Data.GAMES)):
            self.g_b.append(0)

        print(Data.GAMES)

        for i in range(len(Data.GAMES)):
            img = wx.Image(Data.GAMES[i]["icon"], wx.BITMAP_TYPE_ANY)

            W = img.GetWidth()
            H = img.GetHeight()

            new_w = self.max_size
            new_h = self.max_size * H / W
            
            img = img.Scale(new_w, new_h, wx.IMAGE_QUALITY_HIGH)

            bmp = wx.Bitmap(img)

            self.g_b[i] = wx.Button(self, label="", id=i, pos=(50,30), size=(new_w+10, new_h+10))
            self.g_b[i].SetBitmap(bmp)
            self.g_b[i].Bind(wx.EVT_LEFT_DOWN, self.on_game_down)
            self.g_b[i].Bind(wx.EVT_LEFT_UP, self.on_game_up)
            self.g_b[i].Bind(wx.EVT_MOTION, self.on_game_drag)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.g_sizer = wx.GridSizer(6,5,5)

        self.hsizer.Add(add_btn, 0, wx.ALL, 5)
        self.g_sizer.AddMany(self.g_b)
        self.main_sizer.Add(self.hsizer)
        self.main_sizer.Add(self.g_sizer, 0, wx.LEFT, 5)
        self.SetSizer(self.main_sizer)
        self.main_sizer.Fit(self.parent)
        self.SetupScrolling()
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
            for g in Data.GAMES:
                if pathname in g["shortcut"]:
                    wx.MessageBox('Application is already inside your library', 'Error', wx.OK )
                    return
            self.add_game(pathname) 
    
    def on_edit(self, event):
        # add the x on all buttons
        
        if len(self.g_b) != len(Data.GAMES):
            print("tf") 
        
        os.chdir(Path.home())

        edit_svg = wx.svg.SVGimage.CreateFromFile("PlantLauncher/Assets/edit_x.svg")
        bmp = edit_svg.ConvertToBitmap(scale=1 ,width=30, height=30)
        print("self.edit : " + str(self.edit))

        if not self.edit:
            self.e_b = []
            for i in range(len(self.g_b)):
                self.e_b.append(0)
            for i in range(len(self.g_b)):
                self.e_b[i] = wx.Button(self, label="", id=i, size=(30,30), pos=(self.g_b[i].GetPosition()[0] + 75, self.g_b[i].GetPosition()[1] - 5))
                self.e_b[i].Bind(wx.EVT_BUTTON, lambda event: self.on_click(event, i))
                self.e_b[i].SetBitmap(bmp)
                self.e_b[i].SetBitmapMargins((1,1))
        else:
            for i in range(len(self.e_b)):
                self.e_b[i].Destroy()
            self.edit = False
            print(self.e_b)
            return

        self.edit = True

    def on_click(self, event, ind):
            btn = event.GetEventObject()
            btn_id = btn.GetId()
            btn.Destroy()
            Data.GAMES.pop(btn_id)
            self.e_b.pop(btn_id)
            self.g_b[btn_id].Destroy()
            self.g_b.pop(btn_id)
            

    def add_game(self, path):
        """
        adds properties to the game's index in the list and sets up the game in the gui
        """
        self.game = Data.Game()
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

        Data.GAMES.append(self.game)
        self.game.id = Data.GAMES.index(self.game)

        Data.GAMES[self.game.id] = Data.GAMES[self.game.id].to_json()

        self.g_b.append(wx.Button(self, id = self.game.id, label = "", size = (new_w+10, new_h+10), name=str(self.game.id)))
        self.g_b[len(self.g_b) - 1].SetBitmap(bmp)
        if self.edit:
            for i in range(len(self.e_b)):
                self.e_b[i].Destroy()
            self.edit = False
        self.g_b[len(self.g_b) - 1].Bind(wx.EVT_BUTTON, self.on_game_down)
        print(self.game.id)

        self.main_sizer.Remove(self.g_sizer)
        print(Data.GAMES)
        
        self.g_sizer = wx.GridSizer(6,5,5)
        self.g_sizer.AddMany(self.g_b)
        self.main_sizer.Add(self.g_sizer, 0, wx.LEFT, 5)
        self.Layout()
        self.Refresh()
        
    def on_game_down(self, event):
        """
        handles when the user clicks down on a game
        """
        if not self.edit:
            """
            creates a tmp file and dir and creates the launch instructions for the game
            """
            btn = event.GetEventObject()
            btn_id = btn.GetId()

            print(btn_id)

            if not os.path.isdir("/tmp/PlantLauncher"):
                os.makedirs("/tmp/PlantLauncher")
            f = open("/tmp/PlantLauncher/launch_instructions.sh", "a")
            f.write('#!bin/bash')
            f.write("\n" + Data.GAMES[btn_id]["exec"])
            f.close()
            os.chdir(Path.home())
            os.system("bash /tmp/PlantLauncher/launch_instructions.sh")
            os.remove("/tmp/PlantLauncher/launch_instructions.sh")
            os.rmdir("/tmp/PlantLauncher")
            os.chdir(os.path.dirname(__file__))

    def on_game_up(self, event):
        ###check for the nearest cell to reside in (empty or not) and
        ###place object within that cell
        
        print('ash')
    
    def on_game_drag(self, event):
        if self.edit:
            x, y = event.GetPosition()
            if not event.Dragging():
                event.Skip()
                return     
            obj = event.GetEventObject()
            sx,sy = obj.GetPosition()
            dx,dy = wx.GetMousePosition()
            obj.SetPosition(wx.Point(dx-90, dy-190))
            self.e_b[obj.GetId()].SetPosition(wx.Point(dx - 10, dy-195))

            print(dx, dy)
        else:
            return

            
class ConfigTab(scrolled.ScrolledPanel):
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        scrolled.ScrolledPanel.__init__(self, parent, -1)

        title_dir = wx.StaticText(self,  label = "Default Folder")

        dir_b = wx.Button(self, label = "Set Default Game Folder")
        dir_b.Bind(wx.EVT_BUTTON, self.set_dir)

        font = wx.Font(16, family = wx.FONTFAMILY_MODERN, style = 0, weight = 100, 
                      underline = True, faceName ="", encoding = wx.FONTENCODING_DEFAULT)

        title_dir.SetFont(font)

        self.window_size = (545, 300)

        self.resized = False
        parent.Bind(wx.EVT_SIZE, self.OnSize)
        parent.Bind(wx.EVT_IDLE, self.OnIdle)
        self.g_show = wx.Button(self, label="Advanced Options")
        self.g_show.Bind(wx.EVT_BUTTON, self.on_show)

        self.g_titles = []
        self.g_dirs = []
        self.g_exec = []
        self.g_icon = []

        self.refresh_b = wx.Button(self, label = "Refresh", pos=(0 ,0))
        self.refresh_b.SetPosition((self.window_size[0] - self.refresh_b.GetSize()[0] - 5, 0))
        #self.refresh_b.Bind(wx.EVT_BUTTON, self.show_games)
        
        self.dir_txt = wx.TextCtrl(self, size=(200, -1))

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        titledir_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.dir_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.g_sizer = wx.GridSizer(1, 20, 0)

        self.g_sizer.Add(self.g_show, 1, wx.LEFT, 5)
        
        titledir_sizer.Add(title_dir, 0, wx.LEFT, 5)

        self.dir_sizer.Add(dir_b, 0, wx.ALL, 5)
        self.dir_sizer.Add(self.dir_txt, 0, wx.ALL, 5)
        
        self.main_sizer.Add(titledir_sizer, 0, wx.ALL, 5)
        self.main_sizer.Add(self.dir_sizer, 0, wx.ALL, 5)
        self.main_sizer.Add(self.g_sizer, 0, wx.ALL, 5)
        
        self.SetSizer(self.main_sizer)
        self.SetupScrolling()
        self.Layout()
        self.Refresh()

    def OnSize(self,event):
        self.resized = True # set dirty

    def OnIdle(self,event):
        if self.resized: 
            # take action if the dirty flag is set
            
            if self.GetSize()[0] >= 433 and self.GetSize()[1] >= 224:
                self.window_size = self.GetSize()
                self.refresh_b.SetPosition((self.window_size[0] - self.refresh_b.GetSize()[0], 0))
                self.resized = False # reset the flag

    def set_dir(self, event):
        with wx.DirDialog (None, "Choose input directory", "",
                    wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST) as dialog:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return # the user changed their mind

            Data.DEFAULT_GAME_DIR = dialog.GetPath()
            self.dir_txt.SetValue(dialog.GetPath())
    
    def show_games(self, event):
        print('wa')

    def on_show(self, event):
        for i in range(len(self.g_titles)):
            self.g_titles[i].Destroy()
            self.g_dirs[i].Destroy()
            self.g_exec[i].Destroy()
            self.g_icon[i].Destroy()
        for i in range(len(Data.GAMES)):
            self.g_titles.append(0)
            self.g_dirs.append(0)
            self.g_exec.append(0)
            self.g_icon.append(0)
        
        font = wx.Font(12, family = wx.FONTFAMILY_MODERN, style = 0, weight = 100, 
                      underline = True)

        self.main_sizer.Remove(self.g_sizer)
        self.g_sizer = wx.GridSizer(1, 20, 0)
        self.g_sizer.Add(self.g_show, 1, wx.LEFT, 0)

        for i in range(len(Data.GAMES)):
            self.g_titles[i] = wx.StaticText(self, label=Data.GAMES[i]["name"])
            self.g_titles[i].SetFont(font)
            self.g_sizer.Add(self.g_titles[i], 0, wx.LEFT, 0)

            self.g_icon[i] = wx.TextCtrl(self, size=(400, 30), value=Data.GAMES[i]["icon"])
            self.g_sizer.Add(self.g_icon[i], wx.LEFT, 25)

            self.g_dirs[i] = wx.TextCtrl(self, size=(400, 30), value=Data.GAMES[i]["shortcut"])
            self.g_sizer.Add(self.g_dirs[i], wx.LEFT, 25)

            self.g_exec[i] = wx.TextCtrl(self, size=(400, 30), value=Data.GAMES[i]["exec"])
            self.g_sizer.Add(self.g_exec[i], wx.LEFT, 25)

        self.main_sizer.Add(self.g_sizer, 1, wx.ALL, 5)

        self.SetSizer(self.main_sizer)
        self.main_sizer.Fit(self)
        self.Layout()
        self.Refresh()


frame_size = (0,0)