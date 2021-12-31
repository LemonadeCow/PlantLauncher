
import platform
import wx, wx.lib.mixins.inspection
import Tab, Frame

if __name__ == '__main__':
    if "linux" in platform.system().lower():
        app = wx.App(redirect=False)
        frame = Frame.MainFrame()
        frame.SetMinSize(wx.Size(545, 300))
        wx.lib.inspection.InspectionTool().Show()
        app.MainLoop()