import numpy as np
import cv2
import modoscrape
import modoscrape.tools

class SideboardingLocator:

    def __init__(self):
        self.c = modoscrape.Config()
        self.t = modoscrape.tools.Tools
        self.t.showDisabled = True
        self.create_debug = False

    def locate(self, bgr):

        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        card_matches = self.border_threshold(gray)

        if self.create_debug:
            debug = np.copy(bgr)
            for idxc, cm in  enumerate(card_matches):
                px = cv2.cvtColor(cm['pixels'], cv2.COLOR_GRAY2BGR)
                debug = cv2.add(debug, px)

            self.t.show('applied labels&borders', debug)

        return card_matches

    def border_threshold(self, gray):
        im1 = gray.copy()
        im1[im1 == 0] = 255
        im1[im1 < 255] = 0
        kernel = np.ones((2, 2), np.uint8)
        erosion = cv2.erode(im1, kernel, iterations=2)

        # negate black borders, giving white "islands" of card titles
        # or full cards (bottome of stack)
        negative = cv2.bitwise_not(erosion)
        #self.t.show('neg', negative)

        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(negative, connectivity=8)

        card_matches = []
        for label in range(1, num_labels):

            short_side = min(stats[label, cv2.CC_STAT_WIDTH], stats[label, cv2.CC_STAT_HEIGHT])
            long_side = max(stats[label, cv2.CC_STAT_WIDTH], stats[label, cv2.CC_STAT_HEIGHT])
            area = short_side * long_side

            # a card covered by cards stacked on top is arond 128 :  18
            likely_card = False
            ratio = short_side / float(long_side)
            if (ratio > 0.68 and ratio < 0.74 and area > (100 * 220)) or (ratio > 0.12 and ratio < 0.16 and area > (10 * 140) ):

                if self.create_debug:
                    print "border_threshold: label ", label, " wh ", stats[label, cv2.CC_STAT_WIDTH], " ", stats[
                        label, cv2.CC_STAT_HEIGHT], \
                        " at xy ", stats[label, cv2.CC_STAT_LEFT], stats[label, cv2.CC_STAT_TOP]

                #print "   label ", label, "yes"
                likely_card = True
                match = cv2.inRange(labels, label, label)
                match[match >= 1] = 255
                #dilmatch = cv2.dilate(match, np.ones((2, 2), np.uint8), iterations=4)
                info = {'CC_STAT_WIDTH': stats[label, cv2.CC_STAT_WIDTH],
                        'CC_STAT_HEIGHT': stats[label, cv2.CC_STAT_HEIGHT],
                        'CC_STAT_TOP': stats[label, cv2.CC_STAT_TOP],
                        'CC_STAT_LEFT': stats[label, cv2.CC_STAT_LEFT],
                        'pixels': match,
                        'labelid': label,
                        'centroid': centroids[label]
                        }
                #print "match", info
                card_matches.append(info)

        return card_matches




class DialogueLocator:
    def __init__(self):
        self.c = modoscrape.Config()
        self.t = modoscrape.tools.Tools

    def locate(self, bgr, button):

        # only use left 25% of screen, all buttons are there - quicker matching
        # NOTE: slice params are img[y: y + h, x: x + w]
        bgrslice = bgr[0:self.c.CLIENT_HEIGHT, 0:int(self.c.CLIENT_WIDTH / 3)]
        img = cv2.cvtColor(bgrslice, cv2.COLOR_BGR2GRAY)
        templatefile = './img/template_' + button + '.png'

        template = cv2.imread(templatefile, cv2.IMREAD_GRAYSCALE)
        w, h = template.shape[::-1]

        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        self.t.show('match', res)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        top_left = max_loc

        #print 'button', button, max_val, max_loc

        if (max_val > 0.998):
            return max_loc
        else:
            return False

# Locator6: finds active cards that are not touching
class Locator6:

    def __init__(self):
        self.c = modoscrape.Config()
        self.t = modoscrape.tools.Tools
        self.t.showDisabled = True
        self.create_debug = True

    def locate(self, bgr):

        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

        # get black/white card border conn comp
        card_matches = self.border_threshold(gray)

        # get active border lines
        border_matches_v = self.highlight_threshold(gray)

        if self.create_debug:
            debug = np.copy(bgr)
            for idxb, bmv in enumerate(border_matches_v):
                #dil = cv2.dilate(bmv, np.ones((1, 3), np.uint8), iterations=4)
                #debug = debug + cv2.cvtColor(dil, cv2.COLOR_GRAY2BGR)
                px = cv2.cvtColor(bmv['dilpixels'], cv2.COLOR_GRAY2BGR)
                debug = cv2.add(debug, px)
            for idxc, cm in  enumerate(card_matches):
                px = cv2.cvtColor(cm['pixels'], cv2.COLOR_GRAY2BGR)
                debug = cv2.add(debug, px)

            self.t.show('applied labels&borders', debug)

        card_centroids = []
        for idxb, bmv in enumerate(border_matches_v):
            for idxc, cm in  enumerate(card_matches):

                overlap = cv2.bitwise_and(bmv['dilpixels'], cm['pixels'])
                #print bmv['labelid'], "overlap", cm['labelid'], cv2.sumElems(overlap)


                if bmv['labelid'] == 35 and cm['labelid'] == 26:
                    added = cv2.add(bmv['dilpixels'], cm['pixels'])
                    self.t.show('label26', bmv['dilpixels'])
                    self.t.show('label35', cm['pixels'])
                    self.t.show('added',added)


                if (cv2.sumElems(overlap) == (0.0, 0.0, 0.0, 0.0)):
                    pass
                    #print bmv['labelid'], "nomatch with", cm['labelid']
                else:
                    #print "        --> ", idxb, "overlap", idxc, cv2.sumElems(overlap), "centroid", cm['centroid']
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
            #print "border_threshold: label ", label,  " wh ", stats[label, cv2.CC_STAT_WIDTH], " ",  stats[label, cv2.CC_STAT_HEIGHT], \
            #    " at xy ",  stats[label, cv2.CC_STAT_LEFT], stats[label, cv2.CC_STAT_TOP]

            # if the label has a very stretched aspect ratio, and
            short_side = min(stats[label, cv2.CC_STAT_WIDTH], stats[label, cv2.CC_STAT_HEIGHT])
            long_side = max(stats[label, cv2.CC_STAT_WIDTH], stats[label, cv2.CC_STAT_HEIGHT])

            # a upright card is about w 200 : h 280
            likely_card = False
            ratio = short_side / float(long_side)
            if ratio > 0.68 and ratio < 0.74:
                #print "   label ", label, "yes"
                likely_card = True
                match = cv2.inRange(labels, label, label)
                match[match >= 1] = 255
                #dilmatch = cv2.dilate(match, np.ones((2, 2), np.uint8), iterations=4)
                info = {'CC_STAT_WIDTH': stats[label, cv2.CC_STAT_WIDTH],
                        'CC_STAT_HEIGHT': stats[label, cv2.CC_STAT_HEIGHT],
                        'CC_STAT_TOP': stats[label, cv2.CC_STAT_TOP],
                        'CC_STAT_LEFT': stats[label, cv2.CC_STAT_LEFT],
                        'pixels': match,
                        #'dilpixels': dilmatch,
                        'labelid': label,
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
                    #print "highlight_threshold: label ", label, " ", long_side, " x ", short_side, " : candidate at xy",  \
                    #    stats[label, cv2.CC_STAT_LEFT], " ", stats[label, cv2.CC_STAT_TOP]
                    match = cv2.inRange(labels, label, label)
                    match[match >= 1] = 255
                    #border_matches.append(match)
                    dilmatch = cv2.dilate(match, np.ones((3, 3), np.uint8), iterations=3)
                    if stats[label, cv2.CC_STAT_WIDTH] == long_side:
                        info = {'CC_STAT_WIDTH': stats[label, cv2.CC_STAT_WIDTH],
                                'CC_STAT_HEIGHT': stats[label, cv2.CC_STAT_HEIGHT],
                                'CC_STAT_TOP': stats[label, cv2.CC_STAT_TOP],
                                'CC_STAT_LEFT': stats[label, cv2.CC_STAT_LEFT],
                                'pixels': match,
                                'dilpixels': dilmatch,
                                'labelid': label
                                }
                        border_matches_h.append(info)
                    #else:
                     #   border_matches_v.append(info)

        # only use horizontal for now
        return border_matches_h



