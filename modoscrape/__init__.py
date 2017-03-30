import numpy as np
import cv2
import time
import calendar

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
        # print button, " max val ", max_val, " at loc ", max_loc
        # Tools.show('tm_coeff_normed', res)

        if (max_val > 0.999):
            return max_loc
        else:
            return False

            # HSV based color segmentation
            # def dialogue_center00(self, bgr):
            #
            #     hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
            #     lower_blue = np.array([110, 50, 50])
            #     upper_blue = np.array([130, 255, 255])
            #     mask = cv2.inRange(hsv, lower_blue, upper_blue)
            #     res = cv2.bitwise_and(bgr, bgr, mask=mask)
            #
            #     Tools.show('blues', res)
            #     return []

class PixelyLocator:

    def __init__(self):
        self.c = Config()
        self.debug = True

    def locate(self, bgr):
        im0 = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

        Tools.show('gray', im0)

        mode = cv2.TM_CCOEFF_NORMED

        tstart = int(round(time.time() * 1000))
        k = ['right', 'left', 'top', 'bottom']
        matches = {}
        addimg = []

        for side in k:
            template = cv2.imread('./img/ab_' + side + '.png', cv2.IMREAD_GRAYSCALE)
            matches[side] = cv2.matchTemplate(im0, template, mode)
            v  = cv2.inRange(matches[side], 0.987, 100)
            #Tools.show(side, v)
            addimg.append(v)

        im1 = sum(addimg)

        tend = int(round(time.time() * 1000))
        print "dur 4 matches: ", tstart, tend, tend - tstart


        Tools.show('sum', im1)

class ActiveObjectLocator:
    def __init__(self):
        self.c = Config()
        self.debug = True

    def sameish(self, v1, v2):
        if  v1 - v1 * 0.05 <= v2 <= v1 + v1 * 1.05:
            return True
        else:
            return False

    def about_card_height(self, y1, y2):
        len = y2 - y1
        # on 1080p, card is about 200-300px
        if  self.c.CLIENT_HEIGHT / 7 <= len <= self.c.CLIENT_HEIGHT / 3:
            return True
        else:
            return False

    def card_borders(self, gray):
        im1 = gray.copy()
        im1[im1 == 0] = 255
        im1[im1 < 255] = 0
        kernel = np.ones((2, 2), np.uint8)
        erosion = cv2.erode(im1, kernel, iterations=2)
        return erosion

    def active_borders_binimg(self, gray, rangehint):

        rangematches = []

        if rangehint == 'hand':
            # vertical, horizontal main active borders (hand)
            rangematches.append(cv2.inRange(gray, 180, 184))
            rangematches.append(cv2.inRange(gray, 198, 202))

        if rangehint == 'battlefield':
            rangematches.append(cv2.inRange(gray, 208, 212))
            rangematches.append(cv2.inRange(gray, 219, 224))
            rangematches.append(cv2.inRange(gray, 214, 218))
            rangematches.append(cv2.inRange(gray, 205, 209))
            rangematches.append(cv2.inRange(gray, 223, 227))
            rangematches.append(cv2.inRange(gray, 225, 229))

        # contained in bf
        #if rangehint == 'attackers':
        #    rangematches.append(cv2.inRange(gray, 225, 229))
        #    rangematches.append(cv2.inRange(gray, 220, 224 ))

        im1 = sum(rangematches)
        return im1

    def locate(self, bgr):
        im0 = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        imdebug = bgr.copy()
        Tools.show('gray', im0)

        im1 = self.active_borders_binimg(im0, 'battlefield')
        Tools.show('binarized' , im1)

        # morphological op to enhance lines of min length
        vk = np.ones((1, self.c.MIN_CARD_WIDTH), np.uint8)
        erosion_vertical = cv2.erode(im1, vk, iterations=1)

        hk = np.ones((self.c.MIN_CARD_WIDTH, 1), np.uint8)
        erosion_horizontal = cv2.erode(im1, hk, iterations=1)
        im2 = erosion_vertical + erosion_horizontal

        Tools.show('ero', im2)

        borders = self.card_borders(im0)
        Tools.show('borders', borders)

        active_overlap = cv2.bitwise_or(im2, borders)
        Tools.show('overlap', active_overlap)

        click_points = []
        return click_points





class ClickableLocator:
    def __init__(self):
        self.c = Config()
        self.debug = True

    def sameish(self, v1, v2):
        if  v1 - v1 * 0.05 <= v2 <= v1 + v1 * 1.05:
            return True
        else:
            return False

    def about_card_height(self, y1, y2):
        len = y2 - y1
        # on 1080p, card is about 200-300px
        if  self.c.CLIENT_HEIGHT / 7 <= len <= self.c.CLIENT_HEIGHT / 3:
            return True
        else:
            return False

    def clickable_loc(self, bgr, rangehint):
        im0 = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        imdebug = bgr.copy()
        Tools.show('gray', im0)

        rangematches = []

        if rangehint == 'hand':
            # vertical, horizontal main active borders (hand)
            rangematches.append(cv2.inRange(im0, 180, 184))
            rangematches.append(cv2.inRange(im0, 198, 202))

        if rangehint == 'battlefield':
            rangematches.append(cv2.inRange(im0, 208, 212))
            rangematches.append(cv2.inRange(im0, 219, 224))
            rangematches.append(cv2.inRange(im0, 214, 218))
            rangematches.append(cv2.inRange(im0, 205, 209))

        if rangehint == 'attackers':
            rangematches.append(cv2.inRange(im0, 225, 229))
            rangematches.append(cv2.inRange(im0, 220, 224 ))

        im1 = sum(rangematches)
        Tools.show('binarized' , im1)

        # morphological op to enhance lines of min length
        vk = np.ones((1, int(self.c.CLIENT_WIDTH * 0.022)), np.uint8)
        erosion_vertical = cv2.erode(im1, vk, iterations=1)
        print
        hk = np.ones((int(self.c.CLIENT_WIDTH * 0.022), 1), np.uint8)
        erosion_horizontal = cv2.erode(im1, hk, iterations=1)
        im2 = erosion_vertical + erosion_horizontal

        Tools.show('ero' , im2)

        # now from this eroded images with little false positives, select the horizontal lines, check if
        # below it in a reasonable distance is another horizontal line, and if yes, we have our clickable
        # area
        im3, contours, hiera = cv2.findContours(im2, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        if self.debug:
            cv2.drawContours(bgr, contours, -1, (0, 255, 255), 4)


        candidatecontours = []
        for idx, vec in enumerate(contours):
            aspect_ratio = Tools.contour_aspectratio(vec)
            x, y, w, h = cv2.boundingRect(vec)
            if aspect_ratio > 34 and w > (self.c.CLIENT_WIDTH * 0.03):
                print "contour ", idx, " looks like a top/bottom border.", aspect_ratio, w, x, y
                candidatecontours.append(vec)
            else:
                print "contour ", idx, " skipped", aspect_ratio, w, x, y
                pass

        if self.debug:
            cv2.drawContours(bgr, candidatecontours, -1, (255, 20, 20), 4)

        click_points = []
        for idx, vec in enumerate(candidatecontours):
            x, y, w, h = cv2.boundingRect(vec)
            print "candidatecontour ", idx, x, y, w, h, ", looking for matching other end"
            for idx2, vec2 in enumerate(list(candidatecontours)):
                x2, y2, w2, h2 = cv2.boundingRect(vec2)
                print "   comp with ", idx2, x2, y2, w2, h2
                print "   sameish ", self.sameish(x, x2), x, x2, " about ch", self.about_card_height(y, y2), y, y2
                if x == x2 and y == y2:
                    #print "skip comparison with self"
                    continue
                elif self.sameish(x, x2) and self.about_card_height(y, y2):

                    click_x = x + int(w/2)
                    click_y = y2 - int((y2 - y)/2)
                    click_points.append((click_x, click_y))
                    print "    match, point is ", click_x, click_y
                    break


        if self.debug:
            for p in click_points:
                cv2.circle(bgr, p, 10, (255, 0, 30), -1)

        Tools.show('ero', bgr)

        return click_points



class RatioLocator:
    def __init__(self):
        self.c = Config()

    def show(self, t, img):
        cv2.imshow(t, img)
        cv2.waitKey(0)

    def contour_aspectratio(self, c):
        x, y, w, h = cv2.boundingRect(c)
        aspect_ratio = float(w) / h
        return aspect_ratio

    def contour_area(self, c):
        x, y, w, h = cv2.boundingRect(c)
        area = float(w) * h
        return area

    def contour_center(self, c):
        x, y, w, h = cv2.boundingRect(c)
        return [int((x + w) / 2), int((y + h) / 2)]

    def detect_borders(self, cv2im):
        # im00 = cv2.imread('img/screen1.png')
        im00 = cv2im
        im0 = im00.copy()
        im1 = im0.copy()
        im1[im1 == 0] = 255
        im1[im1 < 255] = 0
        # show('input', im0)
        # show('border thresholding', im1)

        kernel = np.ones((2, 2), np.uint8)
        erosion = cv2.erode(im1, kernel, iterations=2)
        canny = cv2.Canny(erosion, 100, 200)
        # show('erosion', erosion)
        # show('canny', canny)

        imc, contours, hierarchy = cv2.findContours(canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        # show('contours', imc)

        candidatecontours = []
        prunedcandidatecontours = []

        # pass 1: add only contours of interesting aspect ratio with no parent
        for idx, vec in enumerate(contours):
            # card aspect ratio uprighg ~ 0.71
            aspect_ratio = self.contour_aspectratio(vec)

            if self.aspect_ratio_test(aspect_ratio) and self.contour_area(vec) > self.c.AREA_MIN:
                bbox = cv2.boundingRect(vec)
                add = True
                for idxc, vecc in enumerate(candidatecontours):
                    existing_bbox = cv2.boundingRect(vecc)
                    if (bbox == existing_bbox):
                        add = False
                        # print "skip candidate ", idx, " same box as ", idxc

                if add:
                    candidatecontours.append(vec)


                    # if (parent_aspect_ratio > 0.68 and parent_aspect_ratio < 0.74):
                    #   candidatecontours.append(vec)
        # print len(candidatecontours), " candidates"

        # now go through all contours and only add these that are not enclosed in antoher one
        for idxi, veci in enumerate(candidatecontours):
            inner = cv2.boundingRect(veci)
            add = True
            for idxo, veco in enumerate(candidatecontours):
                if idxi == idxo:
                    continue
                else:
                    outer = cv2.boundingRect(veco)
                    if (self.union(inner, outer) == outer):
                        # print "--------------------", idxi, idxo
                        # print self.union(inner, outer)
                        # print outer
                        # print idxi, " contained in ", idxo
                        add = False

            if add:
                prunedcandidatecontours.append(veci)

        # i3 = cv2.drawContours(im00, prunedcandidatecontours, -1, (0, 255, 255), 1)
        # show('candidate_contours', i3)
        # cv2.destroyAllWindows()
        return prunedcandidatecontours

    def union(self, a, b):
        x = min(a[0], b[0])
        y = min(a[1], b[1])
        w = max(a[0] + a[2], b[0] + b[2]) - x
        h = max(a[1] + a[3], b[1] + b[3]) - y
        return (x, y, w, h)

    def aspect_ratio_test(self, aspect_ratio):
        if (aspect_ratio > self.c.ASPECT_MIN and aspect_ratio < self.c.ASPECT_MAX):
            # upright card fully visible
            return True
        elif (aspect_ratio < 1 / self.c.ASPECT_MIN and aspect_ratio > 1 / self.c.ASPECT_MAX):
            # tapped card fully visible
            return True
        else:
            return False


class Tools:

    showDisabled = False

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