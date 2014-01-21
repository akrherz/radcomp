# Generate a color ramp image, please
from PIL import Image, ImageDraw, ImageFont
import numpy

font = ImageFont.truetype("/home/akrherz/projects/pyVBCam/lib/veramono.ttf", 10)

ramp = numpy.zeros( (254,3), numpy.uint8)
data = numpy.zeros( (30,256), numpy.uint8)
i = 0
for line in open("iem_lut256.tbl"):
	tokens = line.split()
	ramp[i,0] = int(tokens[0])
	ramp[i,1] = int(tokens[1])
	ramp[i,2] = int(tokens[2])
	data[0:15,i:i+1] = i
	i += 1
ramp[0,0] = 0
ramp[0,1] = 0
ramp[0,2] = 0

png = Image.fromarray( data )
png.putpalette( tuple(ramp.ravel()) )
draw = ImageDraw.Draw(png)

for db in range(-20,100,20):
	x = (db - -31) * 2
	(w,h) = font.getsize(`db`)
	draw.line( [x,17,x,10], fill=255)
	draw.text( (x-(w/2),18), `db`,fill=255, font=font)

draw.text( (235,18), 'dBZ',fill=255, font=font)

#draw.line( [0,0,255,0,255,29,0,29,0,0], fill=255)

png.save("test.png")

