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



class TestLocator6(unittest.TestCase):

    def test_screen5(self):
        tools.showDisabled = True
        bgr = cv2.imread('img/screen5.PNG')
        card_centroids = loc6.locate(bgr)
        self.assertEqual(len(card_centroids), 3, 'unexpected amount of matches')

    def test_screen27(self):
        tools.showDisabled = False
        bgr = cv2.imread('img/screen27.PNG')
        card_centroids = loc6.locate(bgr)
        self.assertEqual(len(card_centroids), 9, 'unexpected amount of matches')

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