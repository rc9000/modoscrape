import numpy as np
import cv2
import time
import calendar
import modoscrape
import modoscrape.tools
import operator

__all__ = ["tools", "locators", "chatbot"]

class Config:
    def __init__(self):
        self.ASPECT_MIN = 0.68
        self.ASPECT_MAX = 0.74
        self.AREA_MIN = 300
        self.CLIENT_WIDTH = 1920
        self.CLIENT_HEIGHT = 1080
        self.CLIENT_X = 0
        self.CLIENT_Y = 0
        self.MIN_CARD_WIDTH = int(self.CLIENT_WIDTH * 0.022)

        #print "calculated values from width ", self.CLIENT_WIDTH, ": min_card_width ", self.MIN_CARD_WIDTH
        self.channel = '#zeroxtwoa'
        self.nickname = 'zeroxtwoa'
        self.server = 'irc.chat.twitch.tv'
        self.port = 6667

class DialogueLocator:
    def __init__(self):
        self.c = Config()

    def locate(self, bgr, button):

        # only use left 25% of screen, all buttons are there - quicker matching
        # NOTE: slice params are img[y: y + h, x: x + w]
        bgrslice = bgr[0:self.c.CLIENT_HEIGHT, 0:int(self.c.CLIENT_WIDTH / 3)]
        img = cv2.cvtColor(bgrslice, cv2.COLOR_BGR2GRAY)
        templatefile = './img/template_' + button + '.png'

        template = cv2.imread(templatefile, cv2.IMREAD_GRAYSCALE)
        w, h = template.shape[::-1]

        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        top_left = max_loc

        if (max_val > 0.999):
            return max_loc
        else:
            return False


class SmartCursor:
    def __init__(self):
        self.c = Config()
        self.t = modoscrape.tools.Tools
        self.relx = 500
        self.rely = 500

    def go(self, coord):
        self.relx = int(coord[0])
        self.rely = int(coord[1])

    def window_corners(self, bgr):
        img = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

        topright = []
        bottomleft = []

        for i, t in enumerate(['close', 'settings']):
            templatefile = './img/template_' + t + '.png'
            template = cv2.imread(templatefile, cv2.IMREAD_GRAYSCALE)
            w, h = template.shape[::-1]
            res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            if (i == 0 and max_val > 0.999):
                topright = max_loc
            elif (i == 1 and max_val > 0.999):
                bottomleft = max_loc

        if topright == [] or bottomleft == []:
            return []

        locprops = {}
        locprops['bottomleft'] = bottomleft
        locprops['bottomleftx'] = bottomleft[0]
        locprops['bottomlefty'] = bottomleft[1]
        locprops['topright'] = topright
        locprops['toprightx'] = topright[0]
        locprops['toprighty'] = topright[1]
        locprops['width'] = topright[0] - bottomleft[0]
        locprops['height'] = bottomleft[1] - topright[1]
        locprops['centerx'] = bottomleft[0] + int(locprops['width']/2)
        locprops['centery'] = topright[1] + int(locprops['height'] / 2.0)


        return locprops

    def label_point(self, i, direction, bgr, pointx, pointy):
        if i == 4 or i == 9 or i == 12:
            if direction == 'R' :
                pointy -= 10
                pointx -= 18
            elif direction == 'L':
                pointy += 30
                pointx -= 18
            elif direction == 'D':
                pointy += 10
                pointx += 5
            elif direction == 'U':
                pointy += 10
                pointx -= 50

            self.t.pointerlabel(bgr, direction + str(i), pointx, pointy)

    def draw(self, bgr):
        # draw cursor and return coordinates
        locprops = self.window_corners(bgr)


        if locprops == []:
            return False

        capturex = self.relx + locprops['bottomleftx']
        capturey = self.rely + locprops['toprighty']
        cursor_markers = {'X': (capturex, capturey), 'R': [], 'L': [], 'D': [], 'U': []}

        self.draw_point(bgr, capturex, capturey, 4, (0, 255, 255))

        step = 8

        # add points to the right, geometrically increasing
        lastx = capturex
        for i in range(1, 1000):
            pointx = lastx + step * i
            if pointx > locprops['toprightx']:
                break
            else:
                lastx = pointx
                cursor_markers['R'].append((pointx, capturey))
                self.draw_point(bgr, pointx, capturey, 4)
                self.label_point(i, 'R', bgr, pointx, capturey)

        # add points to the left, geometrically increasing
        lastx = capturex
        for i in range(1, 1000):
            pointx = lastx - step * i
            if pointx < locprops['bottomleftx']:
                break
            else:
                lastx = pointx
                cursor_markers['L'].append((pointx, capturey))
                self.draw_point(bgr, pointx, capturey, 4)
                self.label_point(i, 'L', bgr, pointx, capturey)

        # add points downwards
        lasty = capturey
        for i in range(1, 1000):
            pointy = lasty + step * i
            if pointy > locprops['bottomlefty']:
                break
            else:
                lasty = pointy
                cursor_markers['D'].append((capturex, pointy))
                self.draw_point(bgr, capturex, pointy, 4)
                self.label_point(i, 'D', bgr, capturex, pointy)

        # add points upwards
        lasty = capturey
        for i in range(1, 1000):
            pointy = lasty - step * i
            if pointy < locprops['toprighty']:
                break
            else:
                lasty = pointy
                cursor_markers['U'].append((capturex, pointy))
                self.draw_point(bgr, capturex, pointy, 4)
                self.label_point(i, 'U', bgr, capturex, pointy)


        self.t.show('cursor drawn', bgr)
        return cursor_markers

    def draw_point(self, bgr, x, y, diameter, color=(255, 255, 255)):

        cv2.circle(bgr, (x, y), diameter + 2, color, -1)
        cv2.circle(bgr, (x, y), diameter + 1, (0, 0, 0), -1)
        cv2.circle(bgr, (x, y), diameter, color, -1)

    # dynamic version of the points in NESW directions above, TODO
    # def point_series(self, originpos,  direction, locprops):
    #
    #     step = 8
    #     pointlist = []
    #
    #     op = operator.sub
    #     if direction == 'W' or direction == 'S':
    #         op = operator.add
    #
    #     calc = {
    #         'E': {'op': operator.add, 'limit:': locprops['toprightx'], 'comp': operator.gt, 'axiscoord': 'y'}
    #     }
    #
    #     lastpos = originpos
    #     for i in range(1, 1000):
    #         op = calc[direction]['op']
    #         point = op(lastpos,  step * i)
    #
    #         if (direction == 'E' and point > locprops['toprightx']):
    #             break
    #         else:
    #             lastpos = point
    #             pointlist.append((point, axiscoord))


