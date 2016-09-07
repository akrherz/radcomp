from PIL import Image
import numpy as np
import sys

img = Image.open(sys.argv[1])

z = np.zeros((256))
r = np.asarray(img)
for d in r.flat:
    z[d] += 1
for i in range(256):
    print i, z[i]
