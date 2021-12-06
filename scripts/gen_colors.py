# Convert Paul's color ramp into 256 levels, maybe

import numpy

rgbz = numpy.zeros((150, 4), "f")

# 256 / 2 = 128
gbase = -32.0
gtop = 95.0
gz = 0.5
i = 0
for line in open("ridge_ref256.tbl"):
    tokens = line.split()
    rgbz[i, 0] = int(tokens[0])
    rgbz[i, 1] = int(tokens[1])
    rgbz[i, 2] = int(tokens[2])
    rgbz[i, 3] = gbase + ((gtop - gbase) * (float(i) / 150.0))
    i += 1

# We want to spread 150 levels to 254
for i in range(254):
    portion = float(i) / 254.0
    look0 = int(portion * 150.0)
    a = numpy.average(rgbz[look0 : (look0 + 2), :], 0)
    print(a)
