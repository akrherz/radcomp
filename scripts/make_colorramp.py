"""Generate a color ramp image, please."""
from PIL import Image, ImageDraw, ImageFont
import numpy as np


def main():
    """Go Main Go."""
    font = ImageFont.truetype(
        "/usr/share/fonts/liberation-mono/LiberationMono-Regular.ttf",
        10,
    )

    ramp = np.zeros((72, 3), np.uint8)
    data = np.zeros((30, 236), np.uint8)
    with open("../gempak/tables/luts/iem_eet.tbl", encoding="ascii") as fh:
        for i, line in enumerate(fh):
            if i == 72:
                break
            if i == 0:
                continue
            tokens = line.split()
            ramp[i, 0] = int(tokens[0])
            ramp[i, 1] = int(tokens[1])
            ramp[i, 2] = int(tokens[2])
            data[0:15, (i * 3) : (i * 3) + 3] = i - 1

    ramp[0, 0] = 0
    ramp[0, 1] = 0
    ramp[0, 2] = 0

    png = Image.fromarray(data)
    png.putpalette(tuple(ramp.ravel()))
    draw = ImageDraw.Draw(png)

    for db in range(10, 71, 10):
        x = (db - 0) * 3 + 3
        (w, _h) = font.getsize(str(db))
        draw.line([x, 17, x, 10], fill=255)
        draw.text((x - (w / 2), 18), str(db), fill=255, font=font)

    draw.text((0, 18), "kft", fill=255, font=font)

    # draw.line( [0,0,255,0,255,29,0,29,0,0], fill=255)

    png.save("test.png")


if __name__ == "__main__":
    main()
