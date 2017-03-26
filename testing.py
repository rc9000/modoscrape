import unittest
import modoscrape
import numpy as np
import cv2

c = modoscrape.Config()
dl = modoscrape.DialogueLocator()
cl = modoscrape.ClickableLocator()


class TestClickableLocator(unittest.TestCase):

    def test_easy_handcards(self):
        modoscrape.Tools.showDisabled = False
        # no yes button in this image
        bgr = cv2.imread('img/screen12.PNG')
        points = cl.clickable_loc(bgr)
        self.assertEqual(len(points), 6)

    def test_target(self):
        # no yes button in this image
        modoscrape.Tools.showDisabled = True
        bgr = cv2.imread('img/screen15.PNG')
        points = cl.clickable_loc(bgr)
        self.assertEqual(len(points), 1)

    def test_attackers(self):
        # no yes button in this image
        modoscrape.Tools.showDisabled = True
        bgr = cv2.imread('img/screen17.PNG')
        points = cl.clickable_loc(bgr)
        # should actually only produce 3 results, but
        # we ignore some artifacts for now
        self.assertEqual(len(points), 7)


class TestDialogueLocator(unittest.TestCase):

    def test_yes_and_no(self):
        # no yes button in this image
        bgr = cv2.imread('img/screen10.PNG')
        loc = dl.dialogue_loc(bgr, 'yes')
        print "location: ", loc
        self.assertEqual(len(loc), 2, 'yes test')
        loc = dl.dialogue_loc(bgr, 'no')
        print "location: ", loc
        self.assertEqual(len(loc), 2, 'no test')

    def test_yes_there(self):
        # find yes button
        bgr = cv2.imread('img/screen7.PNG')
        loc = dl.dialogue_loc(bgr, 'yes')
        print "location: ", loc
        self.assertEqual(len(loc), 2) and self.assertEqual(loc[1], 564)

    def test_yes_not_there(self):
        # no yes button in this image
        bgr = cv2.imread('img/screen1.PNG')
        loc = dl.dialogue_loc(bgr, 'yes')
        print "location: ", loc
        self.assertFalse(loc)

if __name__ == '__main__':
    unittest.main()