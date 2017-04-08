import numpy as np
import cv2
import time
import calendar

class Tools:

    showDisabled = False
    prev_ts = 0

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
    def show(t, img):
        if Tools.showDisabled:
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
    def convert_for_bounding(coords):
        nb_pts = len(coords[0])
        coordz = np.zeros((nb_pts, 2))
        for i in range(nb_pts):
            coordz[i, :] = np.array([int(coords[0][i]), int(coords[1][i])])
        return coordz

    @staticmethod
    # finding width and length of bounding boxes
    def find_wid(xs):
        maxx = 0
        for i in range(4):
            for j in range(i + 1, 4):
                if abs(xs[i] - xs[j]) >= maxx:
                    maxx = abs(xs[i] - xs[j])
        return maxx