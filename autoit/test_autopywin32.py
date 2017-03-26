import win32com.client
autoit = win32com.client.Dispatch("AutoItX3.Control")

x = autoit.WinList()
print x
#autoit.ControlClick(WINDOW, "", "[CLASSNN:TTreeView1]", "left", 1, 53, 41)