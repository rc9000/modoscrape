import numpy as np
from PIL import ImageGrab
import cv2
import modoscrape

while(True):

     # Wide QXGA 2560x1600 left half
     bbox = (0, 0, 1280, 1024)

     pilgrab =  ImageGrab.grab(bbox)
     numpygrab = np.asarray(pilgrab)
     numpygrab = cv2.cvtColor(numpygrab, cv2.COLOR_RGB2BGR)

     lc = modoscrape.Locator()
     im = lc.detect_borders(numpygrab)

     cv2.imshow('window',im)

     if cv2.waitKey(25) & 0xFF == ord('q'):
         cv2.destroyAllWindows()
         break
