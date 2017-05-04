import unittest
import modoscrape
import modoscrape.tools
import modoscrape.locators
import modoscrape.chatbot
import numpy as np
import cv2
import cProfile

c = modoscrape.Config()
tools = modoscrape.tools.Tools()
dl = modoscrape.locators.DialogueLocator()
loc6 = modoscrape.locators.Locator6()
pl = modoscrape.locators.PopupLocator()
sbl = modoscrape.locators.SideboardingLocator()

modoscrape.tools.showDisabled = True

class TestPopupLocator(unittest.TestCase):

    def test_screen42(self):
        modoscrape.tools.showDisabled = True
        bgr = cv2.imread('img/screen42.PNG')
        option_centroids = pl.locate(bgr)
        self.assertEqual(len(option_centroids), 7, 'unexpected amount of matches ' + str(len(option_centroids)) )


class TestSideboardingLocator(unittest.TestCase):

    def test_screen37(self):
        modoscrape.tools.showDisabled = True
        bgr = cv2.imread('img/screen37.PNG')
        card_centroids = sbl.locate(bgr)
        self.assertGreaterEqual(len(card_centroids), 60, 'unexpected amount of matches ' + str(len(card_centroids)) )
        self.assertLessEqual(len(card_centroids), 90, 'unexpected amount of matches ' + str(len(card_centroids)))

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
        modoscrape.tools.showDisabled = True
        center = cursor.draw(bgr)

    def test_draw2(self):
        cursor = modoscrape.SmartCursor()
        cursor.relx = 900
        cursor.rely = 350
        bgr = cv2.imread('img/screen30.PNG')
        modoscrape.tools.showDisabled = True
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

    def test_screen43(self):
        # trying to get rid of dupe matches on grisel and petal in these screens
        modoscrape.tools.showDisabled = True
        bgr = cv2.imread('img/screen43.PNG')
        card_centroids = loc6.locate(bgr)
        self.assertEqual(len(card_centroids), 4, 'unexpected amount of matches ' + str(len(card_centroids)))


class TestDialogueLocator(unittest.TestCase):

    def test_yes_and_no(self):
        modoscrape.tools.showDisabled = True
        # no yes button in this image
        bgr = cv2.imread('img/screen10.PNG')
        loc = dl.locate(bgr, 'yes')
        print "location: ", loc
        self.assertEqual(len(loc), 2, 'yes test')
        loc = dl.locate(bgr, 'no')
        print "location: ", loc
        self.assertEqual(len(loc), 2, 'no test')

    def test_yes_there(self):
        modoscrape.tools.showDisabled = True
        # find yes button
        bgr = cv2.imread('img/screen7.PNG')
        loc = dl.locate(bgr, 'yes')
        print "location: ", loc
        self.assertEqual(len(loc), 2) and self.assertEqual(loc[1], 564)

    def test_yes_not_there(self):
        modoscrape.tools.showDisabled = True
        # no yes button in this image
        bgr = cv2.imread('img/screen1.PNG')
        loc = dl.locate(bgr, 'yes')
        print "location: ", loc
        self.assertFalse(loc)

    def test_begin_sideboarding(self):
        modoscrape.tools.showDisabled = True
        bgr = cv2.imread('img/screen36.PNG')
        loc = dl.locate(bgr, 'sideboarding')
        print "location: ", loc
        self.assertEqual(len(loc), 2)
        self.assertEqual(loc[0], 20)

    def test_begin_sideboarding2(self):
        # white background when the round ends on our turn
        modoscrape.tools.showDisabled = True
        bgr = cv2.imread('img/screen38.PNG')
        loc = dl.locate(bgr, 'sideboarding')
        print "location: ", loc
        self.assertEqual(len(loc), 2)
        self.assertEqual(loc[0], 14)

    def test_submit_sideboard(self):
        modoscrape.tools.showDisabled = True
        bgr = cv2.imread('img/screen35.PNG')
        loc = dl.locate(bgr, 'submit')
        print "location: ", loc
        self.assertEqual(len(loc), 2)
        self.assertEqual(loc[0], 378)

    # def test_rmana(self):
    #     modoscrape.tools.showDisabled = True
    #     bgr = cv2.imread('img/screen40.PNG')
    #     loc = dl.locate(bgr, 'rmana')
    #     print "location: ", loc
    #     self.assertEqual(len(loc), 2)
    #     self.assertEqual(loc[0], 53)

    def test_rmana2(self):
        modoscrape.tools.showDisabled = False
        bgr = cv2.imread('img/screen44.PNG')
        loc = dl.locate(bgr, 'rmana')
        print "location: ", loc
        self.assertEqual(len(loc), 2)
        self.assertEqual(loc[0], 107)



class TestTools(unittest.TestCase):

    def test_aspectratio(self):
        contour = np.array([[[0, 0]], [[0, 10]], [[10,0]], [[10,10]]])
        ar = tools.contour_aspectratio(contour)
        self.assertEqual(ar, 1.0, 'square is not square')

class TestBleepBloop(unittest.TestCase):

    def test_normalize_c(self):
        b = modoscrape.chatbot.BleepBloop
        s = b.normalize_vote("CLICK   C7    ")
        self.assertEqual(s, "click c7", 'normalisation failed')

    def test_normalize_dir(self):
        b = modoscrape.chatbot.BleepBloop
        s = b.normalize_vote("go     l10")
        self.assertEqual(s, "go L10", 'normalisation failed, got ' + s)

    def test_normalize_f(self):
        b = modoscrape.chatbot.BleepBloop
        s = b.normalize_vote("f2")
        self.assertEqual(s, "F2", 'normalisation failed, got ' + s)

    def test_winner(self):
        b = modoscrape.chatbot.BleepBloop

        votes = {
            'a': 'v1',
            'b': 'v3',
            'c': 'v3',
            'd': 'v2',
        }

        winner, count = b.winning_vote(votes)
        self.assertEqual(winner, "v3")

    def test_winner_tied(self):
        b = modoscrape.chatbot.BleepBloop

        votes = {
            'a': 'v1',
            'b': 'v3',
            'c': 'v3',
            'e': 'v3',
            'd': 'v2',
            'f': 'v1',
            'g': 'v1',
        }

        winner, count = b.winning_vote(votes)
        self.assertIn(winner, ['v1', 'v3'])

if __name__ == '__main__':
    unittest.main()