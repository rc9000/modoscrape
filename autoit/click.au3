

#include <Array.au3>
#include <AutoItConstants.au3>

Example()

Func Example()
    ; Retrieve a list of window handles using a regular expression. The regular expression looks for titles that contain the word SciTE or Internet Explorer.
    Local $aWinList = WinList("[REGEXPTITLE:(?i)(.*modern*|.*legacy.*)]")
    ; _ArrayDisplay($aWinList)

    Local $x = $CmdLine[1]
	Local $y = $CmdLine[2]

	;click at 326, 861 (leftmost hand card)
	Local $w = $aWinList[1][0]
	WinActivate($w)
	MouseClick($MOUSE_CLICK_LEFT, $x, $y, 1, 1)

EndFunc   ;==>Example