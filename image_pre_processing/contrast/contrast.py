"""
A simple improvement for the text recognition is to have the input text always be relatively the same thickness.
This is because the neural network is trained on rather thick lines
https://towardsdatascience.com/faq-build-a-handwritten-text-recognition-system-using-tensorflow-27648fb18519

A simple example of how you can increase the contrast of a given image.
"""
import numpy as np
import cv2
from app.word_segmentation import show_image

# read
img = cv2.imread('word_0.png', cv2.IMREAD_GRAYSCALE)

# increase contrast
pxmin = np.min(img)
pxmax = np.max(img)
imgContrast = (img - pxmin) / (pxmax - pxmin) * 255

# increase line width
kernel = np.ones((3, 3), np.uint8)
imgMorph = cv2.erode(imgContrast, kernel, iterations = 1)
show_image(imgMorph)

# write
cv2.imwrite('word_0_thick_2.png', imgMorph)

# TODO find out how to determine what contract works best simple solution -> untill probability is highest
"""
handgeschreven:
normal (handgeschreven.png) => rondgessinsron (0.00012758702)
2 => hondgesteon (0.0049874294)
3 => handgeeteven (0.045786206)
4 =? handgeeteven (0.06114233)
5 => handgeestreven (0.024851194) (lower probability)
6 => handgeestrmsen (0.0033688515)

simple solution -> until probability is highest not secure since he will be more sure with too thick lines.
tekst:
normal (tekst.png) => reist (0.04586883)
2 => test (0.2911346)
3 => test (0.21319734)
4 => tesk (0.0928262)
5 => tst (0.065483086)
6 => #sk (0.1730404)
"""