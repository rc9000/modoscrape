import numpy as np
from PIL import ImageGrab
import cv2
import modoscrape
import time
import calendar
from modoscrape import Tools

FONT = cv2.FONT_HERSHEY_COMPLEX
PAD = 7
FONTCOLOR = (0, 0, 0)
FONTCOLOR2 = (0, 255, 255)

loop = 0
tstart = calendar.timegm(time.gmtime())
rl = modoscrape.RatioLocator()
dl = modoscrape.DialogueLocator()
cl = modoscrape.ClickableLocator()
c = modoscrape.Config()
Tools.showDisabled = True

while (True):

    # modo client in this top left corner
    bbox = (c.CLIENT_X, c.CLIENT_Y, c.CLIENT_WIDTH, c.CLIENT_HEIGHT)

    pilgrab = ImageGrab.grab(bbox)
    numpygrab = np.asarray(pilgrab)
    numpygrab = cv2.cvtColor(numpygrab, cv2.COLOR_RGB2BGR)

    buttons = ['yes', 'no', 'ok', 'cancel', 'keep',  'mulligan', 'done']
    button_locations = {}
    for d in buttons:
        button_locations[d] = dl.dialogue_loc(numpygrab, d)

    boffset = 1
    for b in button_locations:
        if button_locations[b]:
            bx, by = button_locations[b]
            Tools.text(numpygrab, 'b_' + b, bx + 7, by - 7)
            boffset += 1

    points = cl.clickable_loc(numpygrab)
    for i, p in enumerate(points):
        Tools.text(numpygrab, 'c_' + str(i), p[0], p[1])

    cv2.imshow('client capture', numpygrab)

    #cmd = raw_input("command? > ")
    #print "exec: ", cmd, "..."

    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break

    loop += 1
    time.sleep(0.5)
    print "loop iteration", loop
    if (loop % 10) == 0:
        dur =  calendar.timegm(time.gmtime()) - tstart
        print "dur ", dur, (loop / dur), " fps"


