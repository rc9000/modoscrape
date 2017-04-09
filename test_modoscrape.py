import unittest
import modoscrape
import modoscrape.tools
import modoscrape.locators
import numpy as np
import cv2
import cProfile


c = modoscrape.Config()
dl = modoscrape.DialogueLocator()
cl = modoscrape.ClickableLocator()
aol = modoscrape.ActiveObjectLocator()
pl = modoscrape.PixelyLocator()
tools = modoscrape.tools.Tools()
loc5 = modoscrape.locators.Locator5()
loc6 = modoscrape.locators.Locator6()

# class TestActiveObjectLocator(unittest.TestCase):
#
#     def test_attackers(self):
#         # no yes button in this image
#         modoscrape.Tools.showDisabled = False
#         bgr = cv2.imread('img/screen17.PNG')
#         points = aol.locate(bgr)
#         self.assertEqual(len(points), 6)
#
# class TestPixelyLocator(unittest.TestCase):
#
#     def test_attackers(self):
#         # no yes button in this image
#         modoscrape.Tools.showDisabled = False
#         bgr = cv2.imread('img/screen23.PNG')
#         #bgr = cv2.imread('img/screen20.PNG')
#         points = pl.locate(bgr)
#         self.assertEqual(len(points), 6)
#
#
#
# class TestClickableLocator(unittest.TestCase):
#
#     def test_easy_handcards(self):
#         modoscrape.Tools.showDisabled = True
#         # no yes button in this image
#         bgr = cv2.imread('img/screen12.PNG')
#         points = cl.clickable_loc(bgr, 'hand')
#         self.assertEqual(len(points), 6)
#
#     def test_target(self):
#         # no yes button in this image
#         modoscrape.Tools.showDisabled = True
#         bgr = cv2.imread('img/screen15.PNG')
#         points = cl.clickable_loc(bgr, 'battlefield')
#         self.assertEqual(len(points), 1)
#
#     def test_attackers(self):
#         # no yes button in this image
#         modoscrape.Tools.showDisabled = True
#         bgr = cv2.imread('img/screen17.PNG')
#         points = cl.clickable_loc(bgr, 'attackers')
#         # should actually only produce 3 results, but
#         # we ignore some artifacts for now
#         self.assertEqual(len(points), 6)
#
#     def test_20(self):
#         # no yes button in this image
#         modoscrape.Tools.showDisabled = True
#         bgr = cv2.imread('img/screen20.PNG')
#         pointsb = cl.clickable_loc(bgr, 'battlefield')
#         modoscrape.Tools.showDisabled = False
#         pointsh = cl.clickable_loc(bgr, 'hand')
#         self.assertEqual(len(pointsb), 1)
#         # onte too many, but ignore
#         self.assertEqual(len(pointsh), 2)


class TestLocator6(unittest.TestCase):

    def test_basic(self):
        tools.showDisabled = False
        bgr = cv2.imread('img/screen5.PNG')
        loc6.locate(bgr)


class TestLocator5(unittest.TestCase):

    def test_basic(self):
        tools.showDisabled = True
        bgr = cv2.imread('img/screen23.PNG')
        cProfile.runctx('loc5.locate(bgr)', globals(), locals())



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