import os, platform, subprocess, sys
from os.path import exists, isdir, realpath, dirname
import subprocess
import json
from pathlib2 import Path
import wx, wx.lib.scrolledpanel as scrolled
import Data
import urllib.request
from dotenv import load_dotenv, find_dotenv
import time

'''
    ISSUES:
        -No scrolling
        -Windows .exe are not fully supported, well they kinda are now, might make some changes for when the user adds a steam .exe or a lutris .exe
        -.svg are no longer working
        -edit button doesn't work well

    TO-DO:
        -Grid for the games so that they can be moved around freely, like make it magnetized
        -Folders for apps
        -Redesign edit button
        -Use .png instead of .svg 
        -Make the fork of wine optional for the user like the heroic game launcher
        -Fix issues

    IDEAS:
        -Instead of using so many buttons for adding files, maybe use a toolbar with a dropdown menu 
            https://www.geeksforgeeks.org/wxpython-setdropdownmenu-function-in-wx-toolbar/
'''

class GameTab(scrolled.ScrolledPanel):
    
    def __init__(self, parent, icon_size):
        super().__init__(parent)
        print("Entering __init__")
        self.parent = parent # parent is of type notebook

        #scrolled.ScrolledPanel.__init__(self, parent, -1) #scrolling currently not working

        self.PLANT_LAUNCHER_PATH = os.path.realpath(__file__)
        self.PLANT_LAUNCHER_PATH = os.path.dirname(self.PLANT_LAUNCHER_PATH)
        self.PLANT_LAUNCHER_PATH = os.path.dirname(self.PLANT_LAUNCHER_PATH) # basically did ~/PlantLauncher/Launcher/Tab.py -> ../../ -> ~/PlantLauncher
        print(self.PLANT_LAUNCHER_PATH)

        os.chdir(self.PLANT_LAUNCHER_PATH)
        print("changed directory to " + self.PLANT_LAUNCHER_PATH)

        icon = wx.Image(*icon_size)

        self.max_size = 75

        self.add_btn = wx.Button(self, label = "Add .desktop")
        self.add_btn.Bind(wx.EVT_BUTTON, self.on_add)

        self.add_wine_btn = wx.Button(self, label = "Add .exe")
        self.add_wine_btn.Bind(wx.EVT_BUTTON, self.on_add_wine)

        self.edit = False
        self.e_b = []
        self.edit_btn = wx.Button(self, label="Edit")
        self.edit_btn.Bind(wx.EVT_BUTTON, self.on_edit)
        self.edit_btn.SetPosition((self.add_btn.GetPosition()[0] + self.edit_btn.GetSize()[0] + 20, 5)) #fix this tf

        self.add_wine_btn.SetPosition((self.edit_btn.GetPosition()[0] + self.add_wine_btn.GetSize()[0] + 5, 5))
        self.short_path = ""

        os.chdir(self.PLANT_LAUNCHER_PATH)

        # START ACCESSING GAMES STORED IN GAMES.JSON

        print("accessing games.json")

        if exists("Assets/games.json"):
            for line in open("Assets/games.json", "r"):
                if len(line.replace("\\n", "")) > 10:
                    Data.GAMES.append(json.loads(line))
                    print("loaded game to the list")
        else:
            tmp = open("Assets/games.json", "w")
            tmp.write("")
            tmp.close()
            print("no games found in games.json")

        self.g_b = []
        for i in range(len(Data.GAMES)):
            self.g_b.append(0)

        for i in range(len(Data.GAMES)):
            img = wx.Image(Data.GAMES[i]["icon"], wx.BITMAP_TYPE_ANY)

            W = img.GetWidth()
            H = img.GetHeight()

            new_w = int(self.max_size)
            new_h = int(self.max_size * H / W)
            
            img = img.Scale(new_w, new_h, wx.IMAGE_QUALITY_HIGH)

            bmp = wx.Bitmap(img)

            self.g_b[i] = wx.Button(self, label="", id=i, pos=(50,30), size=(new_w+10, new_h+10)) #75 + 10, 75 + 10
            self.g_b[i].SetBitmap(bmp)
            self.g_b[i].Bind(wx.EVT_LEFT_DOWN, self.on_game_down)
            self.g_b[i].Bind(wx.EVT_LEFT_UP, self.on_game_up)
            self.g_b[i].Bind(wx.EVT_MOTION, self.on_game_drag)
            print("Binded the buttons")

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.g_sizer = wx.GridSizer(6,5,5)

        self.hsizer.Add(self.add_btn, 0, wx.ALL, 5)
        self.g_sizer.AddMany(self.g_b)
        self.main_sizer.Add(self.hsizer)
        self.main_sizer.Add(self.g_sizer, 0, wx.LEFT, 5)
        self.SetSizer(self.main_sizer)
        self.main_sizer.Fit(self.parent)
        self.SetupScrolling()
        self.Layout()
        print("Exiting __init__")
    
    def on_add(self, event):
        """
        Button handler for when adding a .desktop file
        """
        print("Entering on_add")
        wildcard = "DESKTOP files (*.desktop)|*.desktop"
        with wx.FileDialog(None, "CHOOSE THE APPLICATION\'S DESKTOP FILES",
                          wildcard = wildcard,
                          style = wx.FD_OPEN) as dialog:
            print("Started FileDialog")
            if dialog.ShowModal() == wx.ID_CANCEL:
                return

            pathname = dialog.GetPath()
            for g in Data.GAMES:
                if pathname in g["shortcut"]:
                    wx.MessageBox("Application is already inside your library", "Error", wx.OK )
                    return
            self.add_game(pathname) 
        print("Exiting on_add")

    def on_add_wine(self, event): #kinda works, might want to use another version of wine or figure out how to use proton on the terminal
        """
        Button handler for when adding a Microsoft .exe file
        """
        print("Entering on_add_wine()")
        wildcard = "EXECUTABLE files (*.exe)|*.exe"
        dlg = wx.FileDialog(self, "ENTER THE APPLICATION\'S .EXE", wildcard = wildcard)
        print("Started dialog")
        if dlg.ShowModal() == wx.ID_OK: 
            path = str("\"" + dlg.GetPath() + "\"")
            os.chdir(self.PLANT_LAUNCHER_PATH)
            if "heroic" not in path.lower():
                self.add_wine(path[path.rindex("/") + 1: len(path) - 5], path, "Assets/wine_icon.png")
            else: # executables imported from heroic will have a different naming scheme
                self.add_wine(os.path.dirname(path)[os.path.dirname(path).rindex("/") + 1: len(os.path.dirname(path))], path, "Assets/wine_icon.png")
        dlg.Destroy()
        print("Destroyed dialog")
        print("Exiting on_add_wine()")

    def on_edit(self, event):
        """
        IDK RN
        I should probably darken the rest of the window and change the color of the main edit button
        """
        print("Entering on_edit()")
        # add the x on all buttons       
        os.chdir(Path.home())

        bmp = wx.Bitmap(self.PLANT_LAUNCHER_PATH + "/Assets/edit.png", wx.BITMAP_TYPE_PNG)
        edit_img = bmp.ConvertToImage()
        bmp = wx.Bitmap(edit_img.Scale(30, 30))

        if not self.edit:
            self.e_b = []
            for i in range(len(self.g_b)):
                self.e_b.append(0)
            for i in range(len(self.g_b)):
                self.e_b[i] = wx.Button(self, label="", id=Data.GAMES[i]["id"], size=(30,30), pos=(self.g_b[i].GetPosition()[0] + 75, self.g_b[i].GetPosition()[1] - 5))
                self.e_b[i].Bind(wx.EVT_BUTTON, lambda event: self.on_click_x(event, i))
                self.e_b[i].SetBitmap(bmp)
                self.e_b[i].SetBitmapMargins((1,1))
            self.edit = True
        else:
            for i in range(len(self.e_b)):
                self.e_b[i].Destroy()
            self.edit = False
            print("Exiting on_edit")
            return
    print("Exiting on_edit")

    def on_click_x(self, event, ind):
        btn = event.GetEventObject()
        Data.GAMES.pop(self.e_b.index(btn))
        self.g_b[self.e_b.index(btn)].Destroy()
        self.g_b.pop(self.e_b.index(btn))
        self.e_b.pop(self.e_b.index(btn))
        btn.Destroy()

    def score(self, str1, str2): # recommendations: figure out how to make it so that the actual length doesn't matter
        """
        Gives a score based on two strings' similarity
        """
        # Ask CC about this !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        count = 0
        str1_l = str1.lower()
        str2_l = str2.lower()
 
        p = False
        for i in range(len(str1_l) - 1):
            for j in range(len(str2_l) - 1):
                if str1_l[i: i+1] == str2_l[j:j+1]:
                    count += 1
                elif (str1_l[i:i+1] == " " or str1_l[i:i+1] == "-" or str1_l[i:i+1] == "_"):
                    i += 1
                    count += 1 #take this out
                elif (str2_l[j:j+1] == " " or str2_l[j:j+1] == "-" or str2_l[j:j+1] == "_"):
                    j += 1
                    count += 1 #take this out
                else:
                    count -= 1
                i += 1
            break
            
        return (count, str1, str2)

    def add_wine(self, name, path_to_exec, path_to_icon):
        """btn = event.GetEventObject()sing wine ofc

        recommendation to myself:
            allow the user to install a version of wine while they upload the file, maybe proton or proton-ge
            
        NOTE: This is the most spaghetti code I have written yet, BEWARE
        """
        print("entering add_wine")
        self.game = Data.Game()
        self.game.name = name
        self.game.icon = path_to_icon
        self.setup_pfx = False

        if not self.setup_pfx and "heroic" in path_to_exec.lower():
            game_path = os.path.dirname(path_to_exec).replace("\"", "") # not sure why that was there
            heroic_path = os.path.dirname(game_path).replace("\"", "")
            print("HEROIC PATH = " + heroic_path)
            print(os.path.isdir(heroic_path))

            # list the directories and find the one with the highest score
            os.chdir(os.path.join(heroic_path, heroic_path + "/Prefixes"))
            max = (0, "", "")
            
            for i in os.listdir():
                n = self.score(game_path, i) # shortest first
                if max[0] < n[0]:
                    max = n
            print("name for directory " + max[-1])
            os.chdir(self.PLANT_LAUNCHER_PATH)

            r = urllib.request.urlopen('https://raw.githubusercontent.com/srdrabx/items-tracker/master/database/list.json')
            tmp = r.read()
            r.close()
            obj = json.loads(str(tmp, 'utf-8'))
            max = (0, "", "")
            index = 0
            for i in range(len(obj)):
                name = obj[i][2]
                n = self.score(name, self.game.name) # it is best to have it ordered as shortest length first since idk how to accomodate for that other than
                                                     # having it set to that in the actual function as in check the one with the least length
                if max[0] < n[0]:
                    print(max)
                    max = n
                    index = i
            print("NAME OF THE CURRENT GAME: " + max[-2])

            g_id = obj[index][0] # the game's id
            print("ID OF THE CURRENT GAME: " + g_id)

            r = urllib.request.urlopen('https://raw.githubusercontent.com/srdrabx/items-tracker/master/database/items/'+ g_id +'.json')
            tmp = r.read()
            r.close()
            obj = json.loads(str(tmp, 'utf-8'))
            self.game.epic_id = obj["releaseInfo"][0]["appId"] # this is the game's app ID, needed to run legendary launch
            print("APPID OF THE CURRENT GAME: " + self.game.epic_id)
            self.game.exec = "mangohud --dlsym /opt/Heroic/resources/app.asar.unpacked/build/bin/linux/legendary launch " + self.game.epic_id + " --wine \"/home/cow/.config/heroic/tools/wine/Wine-GE-Proton7-8/bin/wine\" --wine-prefix \"" + os.path.join(heroic_path, heroic_path + "/Prefixes/" + max[2]) + "\""
            # I'm assuming these games are coming from epic games
            # NOTE: 
                # I should definitely make the wine version customizable, that means I'd have to scan the env variables and look for the paths of the different wine versions and let the user choose
                    # I think that's how that works, I actually don't know tbf
                # and the other settings, mangohud, gamemoderun, dlsym, stuff like that
                # mangohud must be installed beforehand, might make that automated, same with gamemdoderun

                #side note, Mangohud isn't working in "hell is other demons" but seems to work everywhere else, might look into the wineprefix

        self.download_winetricks = False
        if self.download_winetricks and not os.path.isdir(".winetricks"):
            os.makedirs(".winetricks")
            cmd = "cd " + self.PLANT_LAUNCHER_PATH + "/.winetricks && wget  https://raw.githubusercontent.com/Winetricks/winetricks/master/src/winetricks && chmod +x winetricks"
            n = os.popen(cmd)
            if n == 0:
                print("Winetricks has been installed")

        self.download_dxvk = False
        self.dxvk_ver = ""
        self.download_vkd3d = False
        self.vkd3d_ver = ""
        
        if self.download_dxvk:
            print("preparing to download dxvk")
            # fetch version from somewhere
            self.dxvk_ver = "dxvk-1.10.1"
            if not os.path.isdir(".dxvk"):
                os.makedirs(".dxvk")
                os.chdir(self.PLANT_LAUNCHER_PATH + "/.dxvk")
                #I think it'd be smarter to fetch the dxvk version and then insert it here rather than manually setting it, or even better, leaving it to the user
                result = subprocess.Popen(["wget https://github.com/doitsujin/dxvk/releases/download/v" + self.dxvk_ver[5:len(self.dxvk_ver)] + "/" + self.dxvk_ver + ".tar.gz && tar -xvf " + self.dxvk_ver + ".tar.gz && rm -rvf" + self.dxvk_ver + ".tar.gz"], shell=True)
                result.wait()
        os.chdir(self.PLANT_LAUNCHER_PATH)   
        if self.download_vkd3d:
            print("preparing to download vkd3d")
            self.vkd3d_ver = "vkd3d-proton-2.6"
            if not os.path.isdir(".vkd3d"):
                os.makedirs(".vkd3d")
                os.chdir(self.PLANT_LAUNCHER_PATH + "/.vkd3d")
                result = subprocess.Popen(["wget https://github.com/HansKristian-Work/vkd3d-proton/releases/download/v" + self.vkd3d_ver[13:len(self.vkd3d_ver)] + "/" + self.vkd3d_ver + ".tar.zst && tar --use-compress-program=unzstd -xvf " + self.vkd3d_ver + ".tar.zst && rm -rvf " + self.vkd3d_ver + ".tar.zst"], shell=True)
                result.wait()
        os.chdir(self.PLANT_LAUNCHER_PATH)
        '''
        '''
        
        # SETS UP WINEPREFIX
        # A lot of this is unnecessary and should be cleaned up by a competent programmer
        # sadly I have no competent programmer
        if not os.path.isdir(".env"):
            os.makedirs(self.PLANT_LAUNCHER_PATH + "/.env")
        result = subprocess.run(["WINEPREFIX=\"" + self.PLANT_LAUNCHER_PATH + "/.winepfx\""], shell=True)

        print("WINEPREFIX=\"" + self.PLANT_LAUNCHER_PATH + "/.winepfx\"")
        
        f = open(self.PLANT_LAUNCHER_PATH + "/.env/winepfx.env", "w")
        f.write("WINEPREFIX=\"" + self.PLANT_LAUNCHER_PATH + "/.winepfx\"")
        f.close()
        load_dotenv(self.PLANT_LAUNCHER_PATH + "/.env")
        print("loaded .env") # Might not be necessary anymore

        wineprefix = "\"" + self.PLANT_LAUNCHER_PATH + "/.winepfx\""
        print("current wineprefix: " + wineprefix)

        while not os.path.exists(self.PLANT_LAUNCHER_PATH + "/.winepfx/system.reg"):
            print("waiting for the wineprefix to finish loading")
            time.sleep(1)
        error = False
        if self.download_dxvk:
            result = subprocess.run(["bash " + self.PLANT_LAUNCHER_PATH + "/.dxvk/" + self.dxvk_ver + "/setup_dxvk.sh install"], shell=True, capture_output=True)
            if 0 != result.returncode:
                print("error")
                error = True
            else:
                self.download_dxvk = False
        if self.download_vkd3d:
            result = subprocess.run(["bash " + self.PLANT_LAUNCHER_PATH + "/.vkd3d/" + self.vkd3d_ver + "/setup_vkd3d_proton.sh install"], shell=True, capture_output=True)
            if 0 != result.returncode:
                print("error")
                error = True
            else:
                self.download_vkd3d = False
        os.chdir(self.PLANT_LAUNCHER_PATH)

        self.game.exec = "DXVK_HUD=1 WINEPREFIX=" + wineprefix + " wine " + path_to_exec
        if not error:
            print("Wine and wineprfix has been set up")
        else:
            print("Wine and wineprfix has not been correctly set up")

        try:
            bmp = wx.Bitmap(self.game.icon, wx.BITMAP_TYPE_PNG)
            img = bmp.ConvertToImage()

            W = img.GetWidth()
            H = img.GetHeight()
            print("Made image")

            new_w = self.max_size
            new_h = int(self.max_size * H / W)
            
            bmp = wx.Bitmap(img.Scale(new_w, new_h))

            Data.GAMES.append(self.game)
            index = Data.GAMES.index(self.game)
            self.game.id = index + 1000
            ##### FIX THE ID 
            print("Appended game to the Data.GAMES list")

            Data.GAMES[index] = Data.GAMES[index].to_json()
            ##### FIX THE ID
            print("Converted list to json")

            #ADDING THE BUTTON TO THE LIST 

            self.g_b.append(wx.Button(self, id = self.game.id, label = "", size = (new_w+10, new_h+10), name=str(self.game.id)))
            self.g_b[len(self.g_b) - 1].SetBitmap(bmp)
            #if self.edit:
            #    for i in range(len(self.e_b)):
            #        self.e_b[i].Destroy()
            #    self.edit = False
            self.g_b[len(self.g_b) - 1].Bind(wx.EVT_BUTTON, self.on_game_down)
            self.g_b[len(self.g_b) - 1].Bind(wx.EVT_LEFT_UP, self.on_game_up)
            self.g_b[len(self.g_b) - 1].Bind(wx.EVT_MOTION, self.on_game_drag)

            print("added button to list and succesfully binded the button as well")
            #SIZER THINGS 

            self.main_sizer.Remove(self.g_sizer)
            
            self.g_sizer = wx.GridSizer(6,5,5)
            self.g_sizer.AddMany(self.g_b)
            self.main_sizer.Add(self.g_sizer, 0, wx.LEFT, 5)
            self.Layout()
            self.Refresh()
            wx.MessageBox("Game Succesfully Added!", "Wine", wx.OK)
        except:
            #Data.GAMES.pop(self.game.id)
            wx.MessageBox("Either the game has been uninstalled or the icon cannot be found", "Error", wx.OK | wx.ICON_ERROR)    

    def add_game(self, path):
        """
        Sets up games whose information is tied to a .desktop
        """
        self.game = Data.Game()
        self.game.shortcut = path
        desktop_file = open(self.game.shortcut, "r")

        # setup icon
        self.game.icon = subprocess.Popen(["bash", "PlantLauncher/.scripts/get_icon.sh" , self.game.shortcut], cwd=Path.home(), stdout=subprocess.PIPE)
        self.game.icon = str(self.game.icon.stdout.read())
        self.game.icon = self.game.icon.replace("b", "",1)
        self.game.icon = self.game.icon.replace("\\n", "",1)
        self.game.icon = self.game.icon.replace("\"", "")
        self.game.icon = self.game.icon.replace("\'", "")
        print("icon succesfully setup")
        
        #setup exec
        self.game.exec = subprocess.Popen(["bash", "PlantLauncher/.scripts/get_executable.sh" , self.game.shortcut], cwd=Path.home(), stdout=subprocess.PIPE)
        self.game.exec = str(self.game.exec.stdout.readline())
        self.game.exec = self.game.exec.replace("b", "",1)
        self.game.exec = self.game.exec.replace("\\n", "",1)
        self.game.exec = self.game.exec.replace("\"", "")
        self.game.exec = self.game.exec.replace("\'", "")
        print("exec succesfully setup")

        #setup name
        self.game.name = subprocess.Popen(["bash", "PlantLauncher/.scripts/get_name.sh" , self.game.shortcut], cwd=Path.home(), stdout=subprocess.PIPE)
        self.game.name = str(self.game.name.stdout.readline())
        self.game.name = self.game.name.replace("b", "",1)
        self.game.name = self.game.name.replace("\\n", "",1)
        self.game.name = self.game.name.replace("\"", "")
        self.game.name = self.game.name.replace("\'", "")
        print("name succesfully setup")

        desktop_file.close()
        print("desktop_file has been closed")
        
        if "steam_icon_" in self.game.icon or "lutris" in self.game.icon:
            print("current game is a steam or lutris title")

            icon_path = str(Path.home()) + "/.local/share/icons/hicolor/"
            os.chdir(icon_path)
            tmp_dirs = os.listdir()
            tmp_dirs = self.sort(tmp_dirs)

            icon_id = self.game.icon

            for d in tmp_dirs:
                if os.path.isdir(d):
                    if icon_id + ".png" in os.listdir(d + "/apps"):
                        self.game.icon = icon_path + d + "/apps/" + icon_id + ".png"
                        if "128" in d:
                            break     
            print("succesfully found the game icon")

        print(self.game.icon)   
        os.chdir(self.PLANT_LAUNCHER_PATH)         

        try:
            print("Trying...")
            bmp = wx.Bitmap(self.game.icon, wx.BITMAP_TYPE_PNG)
            img = bmp.ConvertToImage()

            W = img.GetWidth()
            H = img.GetHeight()
            print("Made image")

            new_w = self.max_size
            new_h = int(self.max_size * H / W)
            print("Made new size")
            
            bmp = wx.Bitmap(img.Scale(new_w, new_h))
            print("Image is rescaled")

            Data.GAMES.append(self.game)
            index = Data.GAMES.index(self.game)
            self.game.id = index + 1000
            print("Appended game to the Data.GAMES list")
            print(Data.GAMES)

            Data.GAMES[index] = Data.GAMES[index].to_json()
            print("Converted to json")

            self.g_b.append(wx.Button(self, id = self.game.id, label = "", size = (new_w+10, new_h+10)))
            self.g_b[len(self.g_b) - 1].SetBitmap(bmp)
            print("Appended game to the graphical button list")

            # CHECK THIS
            #################################################################################
            if self.edit:
                for i in range(len(self.e_b)):
                    self.e_b[i].Destroy()
                    print("destroyed " + self.e_b[i])
                self.edit = False

            self.g_b[len(self.g_b) - 1].Bind(wx.EVT_BUTTON, self.on_game_down)
            self.g_b[len(self.g_b) - 1].Bind(wx.EVT_LEFT_UP, self.on_game_up)
            self.g_b[len(self.g_b) - 1].Bind(wx.EVT_MOTION, self.on_game_drag)

            self.main_sizer.Remove(self.g_sizer)
            #print("current list " + Data.GAMES)

            self.g_sizer = wx.GridSizer(6,5,5)
            self.g_sizer.AddMany(self.g_b)
            self.main_sizer.Add(self.g_sizer, 0, wx.LEFT, 5)
            self.Layout()
            self.Refresh()
            wx.MessageBox("Game Succesfully Added!", "Wine", wx.OK)
        except:
            #Data.GAMES.pop(self.game.id)
            wx.MessageBox("Either the game has been uninstalled or the icon cannot be found", "Error", wx.OK | wx.ICON_ERROR)
    print("Exiting add_game function")

    def sort(self, list):
        """
        Sorts a list based on a point system that I haven't implemented
        """
        print("Entered the sort function")
        tmp = []

        for d in list:
            if "x" in d and os.path.isdir(d):        
                if int(d[0:d.index("x")]) == int(d[d.index("x") + 1:len(d)]):
                    tmp.append(int(d[0:d.index("x")]))
                else:
                    tmp.append(int(d[d.index("x") + 1:len(d)]))
            else:
                continue
        tmp.sort()

        tmp_1 = []
    
        j = 0
        for j in range(len(tmp)):
            for i in range(len(list)):
                if str(tmp[j]) in list[i]:
                    tmp_1.append(list[i]) #add the numbers, like a scoring system to make this work better

        print("Exited the sort function")
        return tmp_1

    """
    FROM THIS POINT ON EVERYTHING IS UNFINISHED
    """

    def load_games_from_folder(self):
        """
        attempts to load files from a folder
        """
        if Data.DEFAULT_GAME_DIR is not None: # meaning if the directory has been assigned
            os.chdir(self.PLANT_LAUNCHER_PATH + "/Assets")
            '''
            for line in open("Assets/default.json", "r"): 
                if len(line.replace("\\n", "")) > 0 and os.path.isdir(line):
                    os.chdir(line)
                    games = os.listdir(line)
                    for game in games:
                        if ".desktop" in game:
                            self.add_game(game)
                    break
            '''
            os.chdir(self.PLANT_LAUNCHER_PATH)
     
    def on_game_down(self, event):
        """
        handles running the game when the user clicks down on a game

        NOT DONE
        """
        btn = event.GetEventObject()
        if not self.edit: # mental note: figure out how to manage launches so that multiple instances of the same game cannot be launched
            """
            creates a tmp file and dir and creates the launch instructions for the game
            """
            btn = event.GetEventObject()

            if not os.path.isdir("/tmp/PlantLauncher"):
                os.makedirs("/tmp/PlantLauncher")
            f = open("/tmp/PlantLauncher/launch_instructions.sh", "a")
            f.write("#!bin/bash")
            f.write("\n" + Data.GAMES[self.g_b.index(btn)]["exec"])
            f.close()
            os.chdir(Path.home())
            os.system("bash /tmp/PlantLauncher/launch_instructions.sh")
            os.remove("/tmp/PlantLauncher/launch_instructions.sh")
            os.rmdir("/tmp/PlantLauncher")
            os.chdir(self.PLANT_LAUNCHER_PATH)

    def on_game_up(self, event):
        ###check for the nearest cell to reside in (empty or not) and
        ###place object within that cell

        #find the nearest cell, if none close just go to last
        btn = event.GetEventObject()
        self.g_b.append(self.g_b.pop(self.g_b.index(btn)))

        #Data.GAMES.append(Data.GAMES.pop(self.g_b.index(btn)))

        self.main_sizer.Remove(self.g_sizer)

        self.g_sizer = wx.GridSizer(6,5,5)
        self.g_sizer.AddMany(self.g_b)
        self.main_sizer.Add(self.g_sizer, 0, wx.LEFT, 5)
        self.Layout()
        self.Refresh()

        for i in range(len(self.e_b)):
            self.e_b[i].SetPosition((self.g_b[i].GetPosition()[0] + 75, self.g_b[i].GetPosition()[1] - 5))
        
        print("just making sure it works")
    
    def on_game_drag(self, event):
        """
        Just makes it so that the apps can be moved around

        kinda wish it was smoother
        """
        print(event.GetEventObject())
        if not event.Dragging():
            return  
        print("whoooooo")
        
        if self.edit:
            btn = event.GetEventObject()
            bx,by = btn.GetPosition()
            mx,my = wx.GetMousePosition()
            wix,wiy = self.parent.GetParent().GetParent().GetPosition()
            btn.SetPosition((mx - wix - 40, my - wiy - 100))
            self.e_b[self.g_b.index(btn)].SetPosition((bx + 75, by - 5))
            print((bx,by))
        else:
            return

            
class ConfigTab(scrolled.ScrolledPanel):
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        scrolled.ScrolledPanel.__init__(self, parent, -1)
        scrolled.ScrolledPanel.SetupScrolling(self)
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
        self.refresh_b.Bind(wx.EVT_BUTTON, self.show_games)
        
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
        print("I AM SHOWING GAMES :)")

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

            self.g_shortcut_title = wx.StaticText(self, label="Game Location")
            self.g_dirs[i] = wx.TextCtrl(self, size=(400, 30), value=Data.GAMES[i]["shortcut"])
            self.g_sizer.Add(self.g_shortcut_title, wx.LEFT, 25)
            self.g_sizer.Add(self.g_dirs[i], wx.LEFT, 25)

            self.g_icon_title = wx.StaticText(self, label="Icon Location")
            self.g_icon[i] = wx.TextCtrl(self, size=(400, 30), value=Data.GAMES[i]["icon"])
            self.g_sizer.Add(self.g_icon_title, wx.LEFT, 25)
            self.g_sizer.Add(self.g_icon[i], wx.LEFT, 25)

            self.g_exec_title = wx.StaticText(self, label="Execution Arguments")
            self.g_exec[i] = wx.TextCtrl(self, size=(400, 30), value=Data.GAMES[i]["exec"])
            self.g_sizer.Add(self.g_exec_title, wx.LEFT, 25)
            self.g_sizer.Add(self.g_exec[i], wx.LEFT, 25)
        
        self.main_sizer.Add(self.g_sizer, 1, wx.ALL, 5)
        self.SetSizer(self.main_sizer)
        self.main_sizer.Fit(self)
        

        self.Layout()
        self.Refresh()


frame_size = (0,0)