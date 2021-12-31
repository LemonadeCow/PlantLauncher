from pathlib import Path
import os, json
import wx
import Tab, Data

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title='Plant Launcher', size = (545, 300))
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        panel = wx.Panel(self)
        nb = wx.Notebook(panel)
        game_tab = Tab.GameTab(nb, icon_size=(240,240))
        config_tab = Tab.ConfigTab(nb)

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
        for g in Data.GAMES:
            tmp.write("\n" + json.dumps(g))
        tmp.close()
        self.Destroy()