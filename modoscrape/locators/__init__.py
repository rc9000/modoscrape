import numpy as np
import cv2
import modoscrape
import modoscrape.tools


class Locator5:

    def __init__(self):
        self.c = modoscrape.Config()
        self.t = modoscrape.tools.Tools
        self.debug = True



    def locate(self, bgr):
        orig = np.copy(bgr)
        img = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        h, w = img.shape

        img = cv2.inRange(img, 170, 220)

        # finding all components
        self.t.timestamp('...')
        print "foobar"
        nb_edges, output, stats, centroids = cv2.connectedComponentsWithStats(img, connectivity=8)
        self.t.timestamp('connected components')
        size_edges = stats[1:, -1];
        nb_edges = nb_edges - 1
        contours = []
        for i in range(0, nb_edges):
            # eliminating small components
            if size_edges[i] >= 100:
                img2 = np.zeros((h, w))
                img2[output == i + 1] = 255
                contours.append(self.t.convert_for_bounding(cv2.inRange(img2, 254, 255)))

        boxes = []
        # finding bounding rectangle for each component
        for i in range(0, len(contours)):
            c = np.array(contours[i]).astype(int)
            ar = cv2.minAreaRect(c)
            box = cv2.boxPoints(ar)
            box = np.int0([box[:, 1], box[:, 0]]).T
            xs = box[:, 0]
            ys = box[:, 1]
            wid = self.t.find_wid(xs)
            hei = self.t.find_wid(ys)

            # for each rectangle, we'll check if its ratio is like a card one
            card_ratio = 285 / 205
            if hei != 0 and wid != 0:
                if hei / wid <= card_ratio * 1.05 and hei / wid >= card_ratio * 0.95:
                    cv2.drawContours(orig, [box], -1, (0, 0, 255), 2)
                    boxes.append(box)

        self.t.show('L5-1', orig)
        return boxes

    def locate000(self, bgr):


        self.t.show('BorderLocator0', bgr)
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        thresh =  self.border_threshold(gray)
        self.t.show('BorderLocator1', thresh)

        imc, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        # show('contours', imc)

        candidatecontours = []
        prunedcandidatecontours = []

        # pass 1: add only contours of interesting aspect ratio with no parent
        for idx, vec in enumerate(contours):
            aspect_ratio = self.contour_aspectratio(vec)

            if self.aspect_ratio_test(aspect_ratio) and self.contour_area(vec) > self.c.AREA_MIN:
                bbox = cv2.boundingRect(vec)
                add = True
                for idxc, vecc in enumerate(candidatecontours):
                    existing_bbox = cv2.boundingRect(vecc)
                    if (bbox == existing_bbox):
                        add = False

                if add:
                    candidatecontours.append(vec)

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

    def border_threshold(self, gray):
        im1 = gray.copy()
        im1[im1 == 0] = 255
        im1[im1 < 255] = 0
        kernel = np.ones((2, 2), np.uint8)
        erosion = cv2.erode(im1, kernel, iterations=2)
        return erosion




