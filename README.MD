# modoscrape

This is a quick, work-in-progress cv2 prototype of a screenscraper/scriptable controller for MTGO. It's very incomplete but it can identify some cards and buttons the player could interact with.

This is a just for fun project and not intended for public use, but feel free to do with it what you want.

MTGO etc. are trademarks of WOTC.

## requirements

Most of this stuff is painful to install and unable to be put into a nice requirements.txt

 * cv2 (binary install, see http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_setup/py_setup_in_windows/py_setup_in_windows.html)
 * numpy (binary install, must match abi version cv2 is built for), actual versions I am using are numpy-1.10.2-win32-superpack-python2.7.exe with opencv-3.2.0-vc14.exe
 * autoit (not the python modules, actual autoit3.exe from https://www.autoitscript.com/site/autoit/downloads/)
 * PIL ImageGrab (pip, http://pillow.readthedocs.io/en/3.1.x/reference/ImageGrab.html)
 * irc (pip)

