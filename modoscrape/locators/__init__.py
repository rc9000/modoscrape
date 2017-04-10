import numpy as np
import cv2
import modoscrape
import modoscrape.tools

class Locator6:

    def __init__(self):
        self.c = modoscrape.Config()
        self.t = modoscrape.tools.Tools
        #self.t.showDisabled = True
        self.debug = False

    def locate(self, bgr):
        debug = np.copy(bgr)
        #self.t.show('L6.0', bgr)
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
            px = cv2.cvtColor(bmv['dilpixels'], cv2.COLOR_GRAY2BGR)
            debug = cv2.add(debug, px)
            #debug = debug + self.t.gray_to_marker_color(bmv)
        for idxc, cm in  enumerate(card_matches):
            px = cv2.cvtColor(cm['pixels'], cv2.COLOR_GRAY2BGR)
            debug = cv2.add(debug, px)

        self.t.show('applied labels&borders', debug)

        card_centroids = []
        for idxb, bmv in enumerate(border_matches_v):
            for idxc, cm in  enumerate(card_matches):
                #print idxb, "match with", idxc
                overlap = cv2.bitwise_and(bmv['dilpixels'], cm['pixels'])
                #bbin = cv2.threshold(bmv['dilpixels'], 200, 255, cv2.THRESH_BINARY)
                #cbin = cv2.threshold(cm['pixels'], 200, 255, cv2.THRESH_BINARY)
                #overlap = cv2.bitwise_and(bbin, cbin)
                if (cv2.sumElems(overlap) == (0.0, 0.0, 0.0, 0.0)):
                    pass
                else:
                    print "        --> ", idxb, "overlap", idxc, cv2.sumElems(overlap), "centroid", cm['centroid']
                    card_centroids.append(cm['centroid'])


        return card_centroids

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
            if ratio > 0.5 and ratio < 0.74:
                print "card shape test: label ", label, "yes"
                likely_card = True
                match = cv2.inRange(labels, label, label)
                match[match >= 1] = 255
                info = {'CC_STAT_WIDTH': stats[label, cv2.CC_STAT_WIDTH],
                        'CC_STAT_HEIGHT': stats[label, cv2.CC_STAT_HEIGHT],
                        'CC_STAT_TOP': stats[label, cv2.CC_STAT_TOP],
                        'CC_STAT_LEFT': stats[label, cv2.CC_STAT_LEFT],
                        'pixels': match,
                        'centroid': centroids[label]
                        }
                card_matches.append(info)

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

        #border_matches = []
        border_matches_h = []
        #border_matches_v = []
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
                    match[match >= 1] = 255
                    #border_matches.append(match)
                    dilmatch = cv2.dilate(match, np.ones((2, 2), np.uint8), iterations=4)
                    if stats[label, cv2.CC_STAT_WIDTH] == long_side:
                        info = {'CC_STAT_WIDTH': stats[label, cv2.CC_STAT_WIDTH],
                                'CC_STAT_HEIGHT': stats[label, cv2.CC_STAT_HEIGHT],
                                'CC_STAT_TOP': stats[label, cv2.CC_STAT_TOP],
                                'CC_STAT_LEFT': stats[label, cv2.CC_STAT_LEFT],
                                'pixels': match,
                                'dilpixels': dilmatch
                                }
                        border_matches_h.append(info)
                    #else:
                     #   border_matches_v.append(info)

        # only use horizontal for now
        return border_matches_h



