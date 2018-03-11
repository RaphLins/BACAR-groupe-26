"""This is a Simplistic Sign Detector modules.

   A Sign Detector module is a python file that contains a `detect` function
   that is capable of analyzing a color image which, according to the image
   server, likely contains a road sign. The analysis should identify the kind
   of road sign contained in the image.

   See the description of the `detect` function below for more details.
"""

import logging
import numpy as np
import cv2


def detect(bb, sign):
    """This method receives:
    - sign: a color image (numpy array of shape (h,w,3))
    - bb which is the bounding box of the sign in the original camera view
      bb = (x0,y0, w, h) where w and h are the widht and height of the sign
      (can be used to determine e.g., whether the sign is to the left or
       right)
    The goal of this function is to recognize  which of the following signs
    it really is:
    - a stop sign
    - a turn left sign
    - a turn right sign
    - None, if the sign is determined to be none of the above

    Returns: a dictionary dict that contains information about the recognized
    sign. This dict is transmitted to the state machine it should contain
    all the information that the state machine to act upon the sign (e.g.,
    the type of sign, estimated distance).

    This simplistic detector always returns "STOP", copies the bounding box
    to the dictionary.
    """
    (x0, y0, w, h) = bb
    s = [0, 0, 0]
    rg = 0
    rd = 0
    coupage = bb[2] // 2
    pixel = 0
    for line in sign:
        for i in line:
            s[0] += i[0]
            s[1] += i[1]
            s[2] += i[2]
            pixel += 1
    moyenne = s[0] // pixel
    moyenne2 = s[2] // pixel

    if bb[2] > 35 or bb[1] < 13 or bb[3] < 15:
        sign = ""
    elif moyenne > moyenne2:
        panneau_gauche = []
        panneau_droit = []

        for line in sign:
            cc = line[:coupage]
            panneau_gauche.append(cc)
            cc2 = line[coupage:]
            panneau_droit.append(cc2)
        for element in panneau_gauche:
            for i in element:
                rg += i[2]
        for element in panneau_droit:
            for i in element:
                rd += i[2]
        if rg > rd:
            sign = 'left'
        else:
            sign = 'right'
    else:
        sign = 'stop'
    return {'sign': sign, 'x0': x0, 'y0': y0, 'w': w, 'h': h}
