import sys

import numpy as np
from PIL import Image

img = Image.open(sys.argv[1])

z = np.zeros((256))
r = np.asarray(img)
for d in r.flat:
    z[d] += 1
for i in range(256):
    print(i, z[i])
