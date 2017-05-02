

#include <Array.au3>
#include <AutoItConstants.au3>

Click()

Func Click()

    Local $aWinList = WinList("[REGEXPTITLE:(?i)(.*modern*|.*legacy.*)]")
    ;_ArrayDisplay($aWinList)

    Local $x = $CmdLine[1]
	Local $y = $CmdLine[2]
	Local $nClick = $CmdLine[3]
	Local $repeat = $CmdLine[4]

	If $aWinList[0][0] = 0  Then
	    Return
	EndIf

	Local $w = $aWinList[1][0]

	If Not WinActive($w) Then
        WinActivate($w)
    EndIf

    ; seems to cause the double click effect
    For $i = 0 To $repeat
	    MouseClick($MOUSE_CLICK_LEFT, $x, $y, $nClick, 1)
	    Sleep(300)
    Next

	MouseMove($x + 200, $y, 1) ; move mouse off button afterwards, so it doesn't get hover color

EndFunc