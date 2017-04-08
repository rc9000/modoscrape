import numpy as np
from PIL import ImageGrab
import cv2
import modoscrape
import modoscrape.tools
import modoscrape.locators
import time
import calendar


loop = 0
tstart = calendar.timegm(time.gmtime())
dl = modoscrape.DialogueLocator()
cl = modoscrape.ClickableLocator()
c = modoscrape.Config()
loc5 = modoscrape.locators.Locator5()
Tools = modoscrape.tools.Tools()
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
        button_locations[d] = dl.locate(numpygrab, d)

    boffset = 1
    for b in button_locations:
        if button_locations[b]:
            bx, by = button_locations[b]
            Tools.text(numpygrab, 'b_' + b, bx + 7, by - 7 - 30 * boffset)
            boffset += 1

    # for t in ['hand', 'battlefield', 'attackers']:
    #     points = cl.clickable_loc(numpygrab, t)
    #     for i, p in enumerate(points):
    #         Tools.text(numpygrab, t[0:2] + str(i), p[0], p[1])

    boxes5 = loc5.locate(numpygrab)
    for box in boxes5:
        cv2.drawContours(numpygrab, [box], -1, (0, 0, 255), 2)

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


