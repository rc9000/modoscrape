import numpy as np
import cv2
import time
import calendar
import os

showDisabled = True

class Tools:

    #showDisabled = True
    prev_ts = 0
    autoit = "c:/Program Files (x86)/AutoIt3/AutoIt3.exe"

    @staticmethod
    def mouseclick(coord, double_click=False):

        cmd = '"' + Tools.autoit + '"' + ' autoit/click.au3 ' + str(coord[0]) + ' ' + str(coord[1])

        if double_click:
            cmd += ' 2'
        else:
            cmd += ' 1'

        s = os.system(cmd)
        print cmd, s

    @staticmethod
    def fkey(k):

        cmd = '"' + Tools.autoit + '"' + ' autoit/fkey.au3 ' + k
        s = os.system(cmd)
        print cmd, s


    @staticmethod
    def timestamp(text):

        ts = calendar.timegm(time.gmtime())
        print ts
        dur = 0

        if Tools.prev_ts > 0:
            dur = ts - Tools.prev_ts
            print text, dur

        print Tools.prev_ts, ts, dur
        Tools.prev_ts = ts

    @staticmethod
    def text(img, text, x, y):

        FONT = cv2.FONT_HERSHEY_COMPLEX
        FONTCOLOR = (0, 0, 0)
        FONTCOLOR2 = (0, 255, 255)

        cv2.putText(img, text, (x, y), FONT, 1, FONTCOLOR, 3, cv2.LINE_AA)
        cv2.putText(img, text, (x, y), FONT, 1, FONTCOLOR2, 1, cv2.LINE_AA)

    @staticmethod
    def pointerlabel(img, text, x, y):

        FONT = cv2.FONT_HERSHEY_COMPLEX
        FONTCOLOR = (0, 0, 0)
        FONTCOLOR2 = (0, 220, 220)

        cv2.putText(img, text, (x, y), FONT, 1, FONTCOLOR, 2, cv2.LINE_AA)
        cv2.putText(img, text, (x, y), FONT, 1, FONTCOLOR2, 1, cv2.LINE_AA)

    @staticmethod
    def show(t, img):
        global showDisabled
        if showDisabled:
            return
        else:
            stamp = calendar.timegm(time.gmtime())
            fname = 'E:/temp/im' + str(stamp) + ".png"
            print "dump stored as " + fname
            cv2.imwrite(fname, img)
            cv2.imshow(t, img)
            cv2.waitKey(0)

    @staticmethod
    def contour_aspectratio(c):
        x, y, w, h = cv2.boundingRect(c)
        aspect_ratio = float(w) / h
        return aspect_ratio

    @staticmethod
    def contour_area(c):
        x, y, w, h = cv2.boundingRect(c)
        area = float(w) * h
        return area

    @staticmethod
    def contour_center(c):
        x, y, w, h = cv2.boundingRect(c)
        return [int((x + w) / 2), int((y + h) / 2)]

    @staticmethod
    def union(a, b):
        # a,b are cvContour
        x = min(a[0], b[0])
        y = min(a[1], b[1])
        w = max(a[0] + a[2], b[0] + b[2]) - x
        h = max(a[1] + a[3], b[1] + b[3]) - y
        return (x, y, w, h)

    @staticmethod
    def gray_to_marker_color(gray):
        marked = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        marked[marked[:, :, 0] > 0] = 255
        marked[marked[:, :, 1] > 0] = 255
        marked[marked[:, :, 2] > 0] = 0
        return marked