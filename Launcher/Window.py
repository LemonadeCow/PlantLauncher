import os, platform, subprocess, sys
import json
from pathlib import Path
import wx, wx.svg, wx.lib.mixins.inspection, wx.lib.scrolledpanel as scrolled


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

        for line in open(os.getcwd().replace("/Launcher", "") + "/Assets/games.json", "r"):
            if len(line.replace('\\n', '')) > 10:
                data.GAMES.append(json.loads(line))

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
            for g in data.GAMES:
                if pathname in g["shortcut"]:
                    wx.MessageBox('Application is already inside your library', 'Error', wx.OK )
                    return
            self.add_game(pathname) 
    
    def on_edit(self, event):
        # add the x on all buttons
        
        if len(self.g_b) != len(data.GAMES):
            print("tf") 
        
        os.chdir(Path.home())

        edit_svg = wx.svg.SVGimage.CreateFromFile("PlantLauncher/Assets/edit_x.svg")
        bmp = edit_svg.ConvertToBitmap(scale=1 ,width=30, height=30)

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
            print(self.e_b)
            self.edit = False
            return

        self.edit = True

    def on_click(self, event, ind):
            btn = event.GetEventObject()
            btn_id = btn.GetId()
            btn.Destroy()
            data.GAMES.pop(btn_id)
            self.g_b[btn_id].Destroy()
            

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

        data.GAMES[self.game.id] = data.GAMES[self.game.id].to_json()

        self.g_b.append(wx.Button(self, id = 1, label = "", size = (new_w+10, new_h+10), name=str(self.game.id)))
        self.g_b[len(self.g_b) - 1].SetBitmap(bmp)
        if self.edit:
            for i in range(len(self.e_b)):
                self.e_b[i].Destroy()
            self.edit = False
        self.g_b[len(self.g_b) - 1].Bind(wx.EVT_BUTTON, lambda event : self.on_launch(event, self.game.id))
        print(self.game.id)

        self.main_sizer.Remove(self.g_sizer)
        print(data.GAMES)
        
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

            if not os.path.isdir("/tmp/PlantLauncher"):
                os.makedirs("/tmp/PlantLauncher")
            f = open("/tmp/PlantLauncher/launch_instructions.sh", "a")
            f.write('#!bin/bash')
            f.write("\n" + data.GAMES[btn_id]["exec"])
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
        self.g_titles = []
        self.g_dirs = []
        self.g_exec = []
        self.g_icon = []
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

            data.DEFAULT_GAME_DIR = dialog.GetPath()
            self.dir_txt.SetValue(dialog.GetPath())
    
    def show_games(self, event):
        for i in range(len(self.g_titles)):
            self.g_titles[i].Destroy()
            self.g_dirs[i].Destroy()
            self.g_exec[i].Destroy()
            self.g_icon[i].Destroy()
        for i in range(len(data.GAMES)):
            self.g_titles.append(0)
            self.g_dirs.append(0)
            self.g_exec.append(0)
            self.g_icon.append(0)
        
        font = wx.Font(12, family = wx.FONTFAMILY_MODERN, style = 0, weight = 100, 
                      underline = True)

        self.main_sizer.Remove(self.g_sizer)
        self.g_sizer = wx.GridSizer(1, 5, 1)
        for i in range(len(data.GAMES)):
            self.g_titles[i] = wx.StaticText(self, label=data.GAMES[i]["name"])
            self.g_titles[i].SetFont(font)
            self.g_sizer.Add(self.g_titles[i])

            self.g_icon[i] = wx.TextCtrl(self, size=(400, 30), value=data.GAMES[i]["icon"])
            self.g_sizer.Add(self.g_icon[i])

            self.g_dirs[i] = wx.TextCtrl(self, size=(400, 30), value=data.GAMES[i]["shortcut"])
            self.g_sizer.Add(self.g_dirs[i])

            self.g_exec[i] = wx.TextCtrl(self, size=(400, 30), value=data.GAMES[i]["exec"])
            self.g_sizer.Add(self.g_exec[i])

        self.main_sizer.Add(self.g_sizer, 1, wx.LEFT, 10)

        self.SetSizer(self.main_sizer)
        self.main_sizer.Fit(self)
        self.Layout()
        self.Refresh()

frame_size = (0,0)

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title='Plant Launcher', size = (545, 300))
        self.Bind(wx.EVT_CLOSE, self.OnClose)

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
    
    def OnClose(self, event):
        os.chdir(str(Path.home()) + "/PlantLauncher/Assets")
        open("games.json", "w").close()
        tmp = open("games.json", "a")
        for g in data.GAMES:
            tmp.write("\n" + json.dumps(g))
        tmp.close()
        self.Destroy()

if __name__ == '__main__':
    if "linux" in platform.system().lower():
        app = wx.App(redirect=False)
        frame = MainFrame()
        frame.SetMinSize(wx.Size(545, 300))
        wx.lib.inspection.InspectionTool().Show()
        app.MainLoop()
