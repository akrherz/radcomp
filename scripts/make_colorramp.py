# Generate a color ramp image, please
from PIL import Image, ImageDraw, ImageFont
import numpy

font = ImageFont.truetype("/home/akrherz/projects/pyVBCam/lib/veramono.ttf", 10)

ramp = numpy.zeros((72, 3), numpy.uint8)
data = numpy.zeros((30, 216), numpy.uint8)
for i, line in enumerate(open("../gempak/tables/luts/iem_eet.tbl")):
    if i == 72:
        break
    tokens = line.split()
    ramp[i, 0] = int(tokens[0])
    ramp[i, 1] = int(tokens[1])
    ramp[i, 2] = int(tokens[2])
    data[0:15, (i * 3) : (i * 3) + 3] = i

ramp[0, 0] = 0
ramp[0, 1] = 0
ramp[0, 2] = 0

png = Image.fromarray(data)
png.putpalette(tuple(ramp.ravel()))
draw = ImageDraw.Draw(png)

for db in range(10, 71, 10):
    x = (db - 0) * 3 + 3
    (w, h) = font.getsize(str(db))
    draw.line([x, 17, x, 10], fill=255)
    draw.text((x - (w / 2), 18), str(db), fill=255, font=font)

draw.text((0, 18), "kft", fill=255, font=font)

# draw.line( [0,0,255,0,255,29,0,29,0,0], fill=255)

png.save("test.png")
