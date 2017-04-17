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
from pprint import pprint
import traceback


loop = 1
tstart = calendar.timegm(time.gmtime())
dl = modoscrape.DialogueLocator()
c = modoscrape.Config()
cursor = modoscrape.SmartCursor()
loc6 = modoscrape.locators.Locator6()
Tools = modoscrape.tools.Tools()
Tools.showDisabled = True



def do_cmd(cmd, cursor, cursor_points, card_centroids, button_locations):
    tokens = cmd.split(" ")
    print "executing", tokens

    if tokens[0].startswith('F'):
        m = re.search("F(\d)", tokens[0])
        fn = m.group(1)
        if fn in ['2', '4', '6']:
            print "press fkey", fn
            Tools.fkey('F' + fn)
        else:
            print "ignored", tokens[0]

    elif tokens[0] == "go" or tokens[0] == 'click':
        mdir = re.search("^([LRUD])(\d+)", tokens[1])
        mcard = re.search("^(c)(\d+)", tokens[1])
        mbutton = re.search("^(b)(\w+)", tokens[1])

        pprint([mdir, mcard, mbutton])

        if mdir:
            direction = mdir.group(1)
            index = mdir.group(2)

            try:
                coord = cursor_points[direction][int(index)]
                print "action with cursor point", direction, index, coord
                go_or_click(tokens[0], coord, cursor)
            except:
                print "illegal cursor point"
                traceback.print_exc()

        elif mcard:
            prefix = mcard.group(1)
            cardno = mcard.group(2)

            try:
                coord = card_centroids[int(cardno)]
                print "action with card centroid", prefix, cardno, coord
                go_or_click(tokens[0], coord, cursor)
            except:
                print "illegal card centroid, available:"
                traceback.print_exc()
                pprint(card_centroids)

        elif mbutton:
            prefix = mbutton.group(1)
            buttonno = mbutton.group(2)

            try:
                coord = button_locations[int(buttonno)]
                print "action with button", buttonno, coord
                go_or_click(tokens[0], coord, cursor)
            except:
                print "illegal button"
                traceback.print_exc()


def go_or_click(action, coord, cursor):

    if action == "go":
        cursor.go(coord)
    elif action == 'click':
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

    if len(button_locations) >= 1 and loop % 5 == 0:
        cmd = raw_input("(single user) command? > ")
        do_cmd(cmd, cursor, cursor_points, card_centroids, button_locations)

    loop += 1
    print "loop ", loop, "done"




