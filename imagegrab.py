import numpy as np
from PIL import ImageGrab
import cv2
import modoscrape

FONT = cv2.FONT_HERSHEY_SIMPLEX
PAD = 7
FONTCOLOR = (255, 255, 255)

while(True):

     # capture happens in the top left SXGA corner
     bbox = (0, 0, 1280, 1024)

     pilgrab =  ImageGrab.grab(bbox)
     numpygrab = np.asarray(pilgrab)
     numpygrab = cv2.cvtColor(numpygrab, cv2.COLOR_RGB2BGR)

     lctr = modoscrape.Locator()
     contours = lctr.detect_borders(numpygrab)

     numpygrab = cv2.drawContours(numpygrab, contours, -1, (0, 255, 255), 4)

     for idx, vec in enumerate(contours):
         x, y, w, h = cv2.boundingRect(vec)
         cv2.putText(numpygrab, 'c' + str(idx), (x - PAD, y + PAD), FONT, 1, FONTCOLOR, 2, cv2.LINE_AA)

         #cx, cy = lctr.contour_center(vec)
         #label = "center {}x{}".format(cx, cy)
         #cv2.putText(numpygrab, label, (x - PAD, y + PAD + PAD), FONT, 0.5, FONTCOLOR, 1, cv2.LINE_AA)

     cv2.imshow('client capture', numpygrab)

     if cv2.waitKey(25) & 0xFF == ord('q'):
         cv2.destroyAllWindows()
         break
