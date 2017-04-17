import unittest
import modoscrape
import modoscrape.tools
import modoscrape.locators
import numpy as np
import cv2
import cProfile


c = modoscrape.Config()
dl = modoscrape.DialogueLocator()
tools = modoscrape.tools.Tools()
loc6 = modoscrape.locators.Locator6()


modoscrape.tools.showDisabled = False

class TestSmartCursor(unittest.TestCase):

    def test_corners(self):
        cursor = modoscrape.SmartCursor()
        modoscrape.tools.showDisabled = True
        bgr = cv2.imread('img/screen30.PNG')
        locprops = cursor.window_corners(bgr)
        print locprops
        self.assertEqual(locprops['centerx'], 962)
        self.assertEqual(locprops['centery'], 515)

    def test_draw(self):
        cursor = modoscrape.SmartCursor()
        bgr = cv2.imread('img/screen30.PNG')
        modoscrape.tools.showDisabled = False
        center = cursor.draw(bgr)

    def test_draw2(self):
        cursor = modoscrape.SmartCursor()
        cursor.relx = 900
        cursor.rely = 350
        bgr = cv2.imread('img/screen30.PNG')
        modoscrape.tools.showDisabled = False
        center = cursor.draw(bgr)

class TestLocator6(unittest.TestCase):

    def test_screen5(self):
        modoscrape.tools.showDisabled = True
        bgr = cv2.imread('img/screen5.PNG')
        card_centroids = loc6.locate(bgr)
        self.assertEqual(len(card_centroids), 3, 'unexpected amount of matches')

    def test_screen28(self):
        modoscrape.tools.showDisabled = True
        bgr = cv2.imread('img/screen28.PNG')
        card_centroids = loc6.locate(bgr)
        self.assertEqual(len(card_centroids), 3, 'unexpected amount of matches')

class TestDialogueLocator(unittest.TestCase):

    def test_yes_and_no(self):
        # no yes button in this image
        bgr = cv2.imread('img/screen10.PNG')
        loc = dl.locate(bgr, 'yes')
        print "location: ", loc
        self.assertEqual(len(loc), 2, 'yes test')
        loc = dl.locate(bgr, 'no')
        print "location: ", loc
        self.assertEqual(len(loc), 2, 'no test')

    def test_yes_there(self):
        # find yes button
        bgr = cv2.imread('img/screen7.PNG')
        loc = dl.locate(bgr, 'yes')
        print "location: ", loc
        self.assertEqual(len(loc), 2) and self.assertEqual(loc[1], 564)

    def test_yes_not_there(self):
        # no yes button in this image
        bgr = cv2.imread('img/screen1.PNG')
        loc = dl.locate(bgr, 'yes')
        print "location: ", loc
        self.assertFalse(loc)


class TestTools(unittest.TestCase):

    def test_aspectratio(self):
        contour = np.array([[[0, 0]], [[0, 10]], [[10,0]], [[10,10]]])
        ar = tools.contour_aspectratio(contour)
        self.assertEqual(ar, 1.0, 'square is not square')

if __name__ == '__main__':
    unittest.main()