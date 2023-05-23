from xml.etree import ElementTree

import Image
import ImageDraw
import numpy

gbase = -32.0
gz = 0.5

data = numpy.zeros((800, 800), numpy.uint8)
oramp = numpy.zeros((241, 3), "f")
levels = numpy.zeros((255,), "f")
nramp = numpy.zeros((254, 3), numpy.uint8)
for i in range(256):
    y0 = (i % 16) * 50
    x0 = int(i / 16) * 50
    data[x0 : x0 + 50, y0 : y0 + 50] = i
    # data[0:50,i*3:(i+1)*3] = i
png = Image.fromarray(data)
draw = ImageDraw.Draw(png)
# for i in range(256):

doc = ElementTree.XML(open("ReflectivityColorCurveManager.xml", "r").read())


def p(v):
    if v is None:
        return "-"
    return "%.1f" % (float(v),)


def diff(lv, uv):
    if uv is None or lv is None:
        return 0
    return float(uv) - float(lv)


ar = doc.findall("./Level")
ar.reverse()
colors = len(ar)
black = colors
i = 0
for elem in ar:
    uv = elem.attrib.get("upperValue", None)
    if uv:
        levels[i] = float(uv)
    lv = elem.attrib.get("lowerValue", None)
    oramp[i, 0] = int(elem.find("red").text)
    oramp[i, 1] = int(elem.find("green").text)
    oramp[i, 2] = int(elem.find("blue").text)
    y0 = (i % 16) * 50
    x0 = int(i / 16) * 50
    draw.text((y0 + 12, x0 + 15), p(lv), fill=black)
    draw.text((y0 + 12, x0 + 30), p(uv), fill=black)
    i += 1

oramp[i, :] = 0.0


for i in range(1, 254):
    dbz = -31.5 + i * 0.5
    for j in range(len(levels)):
        if levels[j] > dbz:
            break
    if j > 238:
        j = 238
    nramp[i, :] = oramp[j, :]

o = open("iem_lut256.tbl", "w")
for i in range(254):
    o.write(
        "%20s%6.0f %6.0f %6.0f\n" % ("", nramp[i, 0], nramp[i, 1], nramp[i, 2])
    )
o.close()

png.putpalette(tuple(oramp.ravel()))
png.save("ramp.png")
