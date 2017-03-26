import numpy as np
from PIL import ImageGrab
import cv2
import modoscrape
import time
import calendar

FONT = cv2.FONT_HERSHEY_COMPLEX
PAD = 7
FONTCOLOR = (255, 255, 255)
FONTCOLOR2 = (0, 0, 0)

loop = 0
tstart = calendar.timegm(time.gmtime())
rl = modoscrape.RatioLocator()
dl = modoscrape.DialogueLocator()
c = modoscrape.Config()

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
            cv2.putText(numpygrab, 'b_' + b, (bx + PAD, by - boffset * 30), FONT, 1, FONTCOLOR, 2, cv2.LINE_AA)
            cv2.putText(numpygrab, 'b_' + b, (bx + PAD + 2, by - boffset * 30 + 2), FONT, 1, FONTCOLOR2, 1, cv2.LINE_AA)
            boffset += 1

    #print button_locations


    # contours = rl.detect_borders(numpygrab)
    #
    # numpygrab = cv2.drawContours(numpygrab, contours, -1, (0, 255, 255), 4)
    #
    # for idx, vec in enumerate(contours):
    #     x, y, w, h = cv2.boundingRect(vec)
    #     cv2.putText(numpygrab, 'c' + str(idx), (x - PAD, y + PAD), FONT, 1, FONTCOLOR, 2, cv2.LINE_AA)
    #
    #     # cx, cy = lctr.contour_center(vec)
    #     # label = "center {}x{}".format(cx, cy)
    #     # cv2.putText(numpygrab, label, (x - PAD, y + PAD + PAD), FONT, 0.5, FONTCOLOR, 1, cv2.LINE_AA)

    cv2.imshow('client capture', numpygrab)

    #cmd = raw_input("command? > ")
    #print "exec: ", cmd, "..."

    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break

    loop += 1
    time.sleep(0.2)
    print "loop iteration", loop
    if (loop % 10) == 0:
        dur =  calendar.timegm(time.gmtime()) - tstart
        print "dur ", dur, (loop / dur), " fps"


