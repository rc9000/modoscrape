import numpy as np
import cv2

class Locator:

    def __init__(self):
        self.ASPECT_MIN = 0.68
        self.ASPECT_MAX = 0.74
        self.AREA_MIN = 300

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
        #im00 = cv2.imread('img/screen1.png')
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
        #show('contours', imc)

        candidatecontours = []
        prunedcandidatecontours = []

        # pass 1: add only contours of interesting aspect ratio with no parent
        for idx, vec in enumerate(contours):
            # card aspect ratio uprighg ~ 0.71
            aspect_ratio = self.contour_aspectratio(vec)

            if self.aspect_ratio_test(aspect_ratio) and self.contour_area(vec) > self.AREA_MIN:
                bbox = cv2.boundingRect(vec)
                add = True
                for idxc, vecc in enumerate(candidatecontours):
                    existing_bbox = cv2.boundingRect(vecc)
                    if (bbox == existing_bbox):
                        add = False
                        #print "skip candidate ", idx, " same box as ", idxc

                if add:
                    candidatecontours.append(vec)


                    # if (parent_aspect_ratio > 0.68 and parent_aspect_ratio < 0.74):
                    #   candidatecontours.append(vec)
        #print len(candidatecontours), " candidates"

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


        #i3 = cv2.drawContours(im00, prunedcandidatecontours, -1, (0, 255, 255), 1)
        #show('candidate_contours', i3)
        #cv2.destroyAllWindows()
        return prunedcandidatecontours

    def union(self, a, b):
        x = min(a[0], b[0])
        y = min(a[1], b[1])
        w = max(a[0] + a[2], b[0] + b[2]) - x
        h = max(a[1] + a[3], b[1] + b[3]) - y
        return (x, y, w, h)

    def aspect_ratio_test(self, aspect_ratio):
        if (aspect_ratio > self.ASPECT_MIN and aspect_ratio < self.ASPECT_MAX):
            # upright card fully visible
            return True
        elif (aspect_ratio < 1 / self.ASPECT_MIN and aspect_ratio > 1 / self.ASPECT_MAX):
            # tapped card fully visible
            return True
        else:
            return False
