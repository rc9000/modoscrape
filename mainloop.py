import numpy as np
from PIL import ImageGrab
import cv2
import modoscrape
import modoscrape.tools
import modoscrape.locators
import time
import calendar
import math
import re


loop = 0
tstart = calendar.timegm(time.gmtime())
dl = modoscrape.DialogueLocator()
c = modoscrape.Config()
cursor = modoscrape.SmartCursor()
loc6 = modoscrape.locators.Locator6()
Tools = modoscrape.tools.Tools()
Tools.showDisabled = True



def do_cmd(cmd, cursor, cursor_points):
    tokens = cmd.split(" ")
    print "executing", tokens
    if tokens[0] == "go" or tokens[0] == 'click':
        m = re.search("([LRUD])(\d+)", tokens[1])
        direction = m.group(1)
        index = m.group(2)

        try:
            coord = cursor_points[direction][int(index)]
        except:
            print "illegal cursor point"
            return

        print "action with cursor point", direction, index, coord

        if tokens[0] == "go":
            cursor.go(coord)
        elif tokens[0] == 'click':
            cursor.go(coord)
            Tools.mouseclick(coord)

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
            Tools.text(numpygrab, 'b' + b, bx + 7, by - 7 - 30 * boffset)
            boffset += 1

    card_centroids = loc6.locate(numpygrab)
    for idx, centroid in enumerate(card_centroids):
        Tools.text(numpygrab, 'c' + str(idx), int(centroid[0]), int(centroid[1]))

    cursor_points = cursor.draw(numpygrab)

    cv2.imshow('client capture', numpygrab)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break


    time.sleep(0.1)

    if len(button_locations) >= 1 and loop % 20 == 0:
        cmd = raw_input("(single user) command? > ")
        do_cmd(cmd, cursor, cursor_points)

    loop += 1
    print "loop ", loop, "done"




