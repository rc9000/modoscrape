#AutoIt3Wrapper_Change2CUI=y
#include <Array.au3>
#include <AutoItConstants.au3>

; compile:
; "C:\Program Files (x86)\AutoIt3\SciTE\..\aut2exe\aut2exe.exe" /in windowlist.au3 /console

Click()

Func Click()

    ;Local $aWinList = WinList("[REGEXPTITLE:(?i)(.*)]")
    Local $aWinList = WinList("[REGEXPTITLE:(?i)(.*modern*|.*legacy.*|Magic. The Gathering)]")

    ;_ArrayDisplay($aWinList)

    ConsoleWrite($aWinList[1][0] & @CRLF)
	For $i = 1 To $aWinList[0][0] Step 1
	   ConsoleWrite($aWinList[$i][1] & ' ' & $aWinList[$i][0] & @CRLF)
    Next
EndFunc