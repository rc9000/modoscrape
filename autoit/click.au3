

#include <Array.au3>
#include <AutoItConstants.au3>

Click()

Func Click()

    Local $aWinList = WinList("[REGEXPTITLE:(?i)(.*modern*|.*legacy.*)]")
    ; _ArrayDisplay($aWinList)

    Local $x = $CmdLine[1]
	Local $y = $CmdLine[2]

	Local $w = $aWinList[1][0]

	If Not WinActive($w) Then
        WinActivate($w)
    EndIf

	MouseClick($MOUSE_CLICK_LEFT, $x, $y, 1, 1)

EndFunc