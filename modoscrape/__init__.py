import numpy as np
import cv2
import time
import calendar

__all__ = ["tools", "locators"]

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


