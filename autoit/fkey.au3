

#include <Array.au3>
#include <AutoItConstants.au3>

Fkey()

Func Fkey()

    Local $aWinList = WinList("[REGEXPTITLE:(?i)(.*modern*|.*legacy.*)]")
    Local $k = $CmdLine[1]

	Local $w = $aWinList[1][0]
	WinActivate($w)
	Send("{" & $k & "}")

EndFunc