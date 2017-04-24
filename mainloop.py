import numpy as np
from PIL import ImageGrab
import cv2
import modoscrape
import modoscrape.tools
import modoscrape.locators
import modoscrape.chatbot
import time
import calendar
import math
import re
from pprint import pprint
import traceback
import threading
import random
import urllib
import json


c = modoscrape.Config()
dl = modoscrape.locators.DialogueLocator()
loc6 = modoscrape.locators.Locator6()
sbl = modoscrape.locators.SideboardingLocator()
cursor = modoscrape.SmartCursor()
Tools = modoscrape.tools.Tools()
Tools.showDisabled = True
#mode = 'singleuser'
mode = 'irc'
#mode = 'passive'


def main():

    loop = 1
    bot = False
    viewer_count = 1

    if mode == 'irc':
        bot = modoscrape.chatbot.BleepBloop()
        bot_thread = threading.Thread(target=bot.start)
        bot_thread.start()
        time.sleep(3) # wait for irc connection
        viewer_count = fetch_viewer_count()

    while (True):

        # modo client in this top left corner
        bbox = (c.CLIENT_X, c.CLIENT_Y, c.CLIENT_WIDTH, c.CLIENT_HEIGHT)

        pilgrab = ImageGrab.grab(bbox)
        numpygrab = np.asarray(pilgrab)
        numpygrab = cv2.cvtColor(numpygrab, cv2.COLOR_RGB2BGR)

        buttons = ['yes', 'no', 'ok', 'cancel',
                   'keep',  'mulligan', 'done', 'cmana',
                   'sideboarding', 'submit', 'lobby' ]

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

        sb_centroids = []
        if button_locations['submit']:
            sb_centroids = sbl.locate(numpygrab)
            for idx, centroid in enumerate(sb_centroids):
                xoff = 30
                if idx % 2 == 0:
                    xoff *= -1
                    xoff -= 10
                Tools.text(numpygrab, 's' + str(idx),  int(centroid[0]) + xoff, int(centroid[1]))


        cursor_points = cursor.draw(numpygrab)

        cv2.imshow('client capture', numpygrab)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

        time.sleep(0.1)

        if len(button_locations) >= 1:   #and loop % 5 == 0:

            if mode == 'singleuser':
                cmd = raw_input("(single user) command? > ")
                do_cmd(cmd, cursor, cursor_points, card_centroids, button_locations, sb_centroids)
            elif mode == 'irc':
                # this should be async... just poll a flag in the bot if a vote is ongoing,
                # and if there is a vote result available process it, then start a new vote

                state = bot.state_check(viewer_count)
                if (state == bot.STATE_RESULT_READY):
                    winner, sorted_tally = bot.end_vote()
                    do_cmd(winner, cursor, cursor_points, card_centroids, button_locations, sb_centroids)

                if loop % 30 == 0:
                    print "updating viewer count..."
                    viewer_count = fetch_viewer_count()

            else:
                # no voting, just run CV loop
                pass


        loop += 1

        if loop % 21 == 0:
            print "cycle", loop, ":", random.choice(c.progress_msg)



def do_cmd(cmd, cursor, cursor_points, card_centroids, button_locations, sb_centroids):
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

    elif tokens[0] == "pass":
        print "pass until next update"
        return

    elif tokens[0] == "clickchoice":
        mcard = re.search("^clickchoice (c)(\d+) (\d)", cmd)
        print "mcard", mcard
        if mcard:
            prefix = mcard.group(1)
            cardno = mcard.group(2)
            choice = mcard.group(3)

            # click multi-color land, planeswalker etc. option
            # must keep the window active between the first and the second click,
            # so this special command is required in single user mode
            line_height = 28

            try:
                coord = card_centroids[int(cardno)]
                print "clickchoice", prefix, cardno, choice
                go_or_click("click", coord, cursor, True, False)
                time.sleep(0.2)
                go_or_click("click", (coord[0] + 10, coord[1] + 5 + (int(choice) - 1) * line_height), cursor, True, False)
            except:
                print "illegal card centroid, available:"
                traceback.print_exc()
                pprint(card_centroids)

    elif tokens[0] == "go" or tokens[0] == 'click':
        mdir = re.search("^([LRUD])(\d+)", tokens[1])
        mcard = re.search("^(c)(\d+)", tokens[1])
        mbutton = re.search("^(b)(\w+)", tokens[1])
        msbcard = re.search("^(s)(\d+)", tokens[1])

        pprint([mdir, mcard, mbutton])

        if mdir:
            direction = mdir.group(1)
            index = mdir.group(2)

            try:
                coord = cursor_points[direction][int(index)]
                print "action with cursor point", direction, index, coord
                go_or_click(tokens[0], coord, cursor, True, False)
            except:
                print "illegal cursor point"
                traceback.print_exc()

        elif msbcard:
            prefix = mcard.group(1)
            cardno = mcard.group(2)

            try:
                coord = sb_centroids[int(cardno)]
                print "action with sbcard centroid", prefix, cardno, coord
                go_or_click(tokens[0], coord, cursor, True, True)
            except:
                print "illegal sbcard centroid, available:"
                traceback.print_exc()
                pprint(sb_centroids)

        elif mcard:
            prefix = mcard.group(1)
            cardno = mcard.group(2)

            try:
                coord = card_centroids[int(cardno)]
                print "action with card centroid", prefix, cardno, coord
                go_or_click(tokens[0], coord, cursor, True, False)
            except:
                print "illegal card centroid, available:"
                traceback.print_exc()
                pprint(card_centroids)

        elif mbutton:
            prefix = mbutton.group(1)
            buttonname = mbutton.group(2)
            pprint(button_locations)

            try:
                coord = button_locations[buttonname]
                print "action with button", buttonname, coord
                if not coord:
                    print "unknown/not visible button", buttonname
                    return
                go_or_click(tokens[0], (coord[0] + 10, coord[1] + 10) , cursor, False, False)
            except:
                print "illegal button"
                traceback.print_exc()
    else:
        print "unknown command", tokens


def go_or_click(action, coord, cursor, go_when_clicked, double_click):

    if action == "go":
        cursor.go(coord)
    elif action == 'click':
        if go_when_clicked:
            cursor.go(coord)
        Tools.mouseclick(coord, double_click)


def fetch_viewer_count():
    url = "https://tmi.twitch.tv/group/user/phyrexianviewbot/chatters"
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    print data['chatter_count']
    return int(data['chatter_count'])


if __name__ == '__main__':
        main()
