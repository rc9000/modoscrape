import numpy as np
import cv2
import modoscrape
import modoscrape.tools

class Locator6:

    def __init__(self):
        self.c = modoscrape.Config()
        self.t = modoscrape.tools.Tools
        self.debug = True

    def locate(self, bgr):
        debug = np.copy(bgr)
        self.t.show('L6.0', bgr)
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

        # get black/white card border conn comp
        card_matches = self.border_threshold(gray)
        #self.t.show('L6.1', cardborders)

        # get active border lines
        border_matches_v = self.highlight_threshold(gray)
        #self.t.show('L6.2', activeborders)

        for idxb, bmv in enumerate(border_matches_v):
            #dil = cv2.dilate(bmv, np.ones((1, 3), np.uint8), iterations=4)
            #debug = debug + cv2.cvtColor(dil, cv2.COLOR_GRAY2BGR)
            debug = debug + cv2.cvtColor(bmv, cv2.COLOR_GRAY2BGR)
            #debug = debug + self.t.gray_to_marker_color(bmv)
        for idxc, cm in  enumerate(card_matches):
            debug = debug + cv2.cvtColor(cm, cv2.COLOR_GRAY2BGR)

        self.t.show('applied labels&borders', debug)

        for idxb, bmv in enumerate(border_matches_v):

            dk = np.ones((1, 3), np.uint8)
            im3 = cv2.dilate(bmv, dk, iterations=2)

            for idxc, cm in  enumerate(card_matches):
                print "foo"
                # if a vertical border is close to a card match, consider this point clickable





            #cardborders = cardborders + a
            #self.t.show('apply label' + str(idx), cardborders)
            #self.t.show('apply label' + str(idx), a)
            #if (idx >= 5):
            #    break

        #self.t.show('applied labels', cardborders)
        # overlay both



    def border_threshold(self, gray):
        im1 = gray.copy()
        im1[im1 == 0] = 255
        im1[im1 < 255] = 0
        kernel = np.ones((2, 2), np.uint8)
        erosion = cv2.erode(im1, kernel, iterations=2)

        # now only match borders that look like a card or other interesting object
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(erosion, connectivity=8)

        card_matches = []
        for label in range(1, num_labels):
            print "card shape test: label ", label,  " ", stats[label, cv2.CC_STAT_WIDTH], " ",  stats[label, cv2.CC_STAT_HEIGHT]

            # if the label has a very stretched aspect ratio, and
            short_side = min(stats[label, cv2.CC_STAT_WIDTH], stats[label, cv2.CC_STAT_HEIGHT])
            long_side = max(stats[label, cv2.CC_STAT_WIDTH], stats[label, cv2.CC_STAT_HEIGHT])

            # a upright card is about w 200 : h 280
            likely_card = False
            ratio = short_side / float(long_side)
            if ratio > 0.68 and ratio < 0.74:
                likely_card = True
                match = cv2.inRange(labels, label, label)
                match[match >= 1] = 255
                card_matches.append(match)




        return card_matches


    def highlight_threshold(self, gray):
        im1 = gray.copy()
        im2 = cv2.inRange(im1, 178, 240)
        self.t.show('L6.2 range', im2)
        # morphological op to enhance lines of min length
        vk = np.ones((1, self.c.MIN_CARD_WIDTH), np.uint8)
        erosion_vertical = cv2.erode(im2, vk, iterations=2)

        hk = np.ones((50, 1), np.uint8)
        erosion_horizontal = cv2.erode(im2, hk, iterations=2)
        im3 = erosion_vertical + erosion_horizontal


        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(im3, connectivity=8)
        #self.t.show('L6.3 conncomst', output)

        border_matches = []
        border_matches_h = []
        border_matches_v = []
        # iterate through all labels and find relevant items
        for label in range(1, num_labels):
            #print "cc: label ", label,  " ", stats[label, cv2.CC_STAT_WIDTH], " ",  stats[label, cv2.CC_STAT_HEIGHT]
            # if the label has a very stretched aspect ratio, and
            short_side = min(stats[label, cv2.CC_STAT_WIDTH], stats[label, cv2.CC_STAT_HEIGHT])
            long_side = max(stats[label, cv2.CC_STAT_WIDTH], stats[label, cv2.CC_STAT_HEIGHT])

            if long_side > 20 and long_side < 300:
                if short_side <= 4:
                    # TBD: maybe separate vertical / horizontal matches here already
                    print "cc: label ", label, " ", long_side, " x ", short_side, " : candidate at xy",  \
                        stats[label, cv2.CC_STAT_LEFT], " ", stats[label, cv2.CC_STAT_TOP]
                    match = cv2.inRange(labels, label, label)
                    match[match >= 1] = 200
                    border_matches.append(match)
                    if stats[label, cv2.CC_STAT_WIDTH] == long_side:
                        border_matches_h.append(match)
                    else:
                        border_matches_v.append(match)

        # only use horizontal for now
        return border_matches_h


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




