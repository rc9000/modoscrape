# modoscrape aka Twitch Plays MTGO!

Some very flaky computer vision made love to an IRC bot.

This is a just for fun project and not intended for public use, but feel free to do with it what you want.

MTGO etc. are trademarks of WOTC.

## requirements

Most of this stuff is painful to install and unable to be put into a nice requirements.txt

 * cv2 (binary install, see http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_setup/py_setup_in_windows/py_setup_in_windows.html)
 * numpy (binary install, must match abi version cv2 is built for), actual versions I am using are numpy-1.10.2-win32-superpack-python2.7.exe with opencv-3.2.0-vc14.exe
 * autoit (not the python modules, actual autoit3.exe from https://www.autoitscript.com/site/autoit/downloads/)
 * PIL ImageGrab (pip, http://pillow.readthedocs.io/en/3.1.x/reference/ImageGrab.html)
 * irc (pip)

# How To Play

You can vote for the next game action by just typing in the chat, as soon as the bot prompts for it.

## Objects

Some cards and buttons are automatically labeled, e.g. cards as c*number* or buttons as b*name*. You can vote to click such an object by typing e.g.

    click c4

Besides `click`, there is also a `go` command that only moves the center of the cursor to the location.

## Cursor

To click something without a direct label, the cross-shaped cursor can be used. The middle dot is called `X`, and the points in up, right, down, left direction can be called with `u4`, `d2` and so on. For the dots without a text next to it, just count from the nearest labeled dot. Some examples.

    click x
    go d4
    click r8

## F-Keys

Using F-keys is usually the best way to operate the client. Supported commands:

    F2
    F4
    F6

