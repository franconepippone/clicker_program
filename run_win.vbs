' === run_silent.vbs ===
Set fso = CreateObject("Scripting.FileSystemObject")

' Get folder where this .vbs file lives
curDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Build paths
pythonExe = curDir & "\.venv\Scripts\pythonw.exe"
scriptPath = curDir & "\src\main.py"

' Create shell object
Set shell = CreateObject("WScript.Shell")

' Run the script silently (0 = hidden window, False = don’t wait)
shell.Run """" & pythonExe & """ """ & scriptPath & """", 0, False
