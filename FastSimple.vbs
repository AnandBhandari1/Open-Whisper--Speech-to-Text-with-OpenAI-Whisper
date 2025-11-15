' FastSimple - Silent Launcher (no console window)
' This launches the app without showing a command prompt

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
strScriptPath = WScript.ScriptFullName
strScriptDir = objFSO.GetParentFolderName(strScriptPath)

' Path to the batch file
strBatchFile = strScriptDir & "\run_win.bat"

' Check if batch file exists
If objFSO.FileExists(strBatchFile) Then
    ' Run the batch file hidden (0 = hidden window)
    objShell.Run """" & strBatchFile & """", 0, False
Else
    MsgBox "Error: run_win.bat not found in " & strScriptDir, vbCritical, "FastSimple Error"
End If
