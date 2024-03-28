"""Generate a color ramp image, please."""

import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def get_values(prod):
    """Get value array."""
    values = []
    with open("gempak/tables/unidata/nex2gini.tbl", encoding="ascii") as fh:
        for line in fh:
            if not line.startswith(prod):
                continue
            meat = line.split()[3].split(",", maxsplit=1)[1]
            for block in meat.split(";"):
                tokens = block.split(",")
                startval = float(tokens[2])
                endval = float(tokens[3])
                cnt = int(tokens[1]) - int(tokens[0])
                if startval < -100 and cnt == 1:
                    values.append(None)
                    continue
                dx = (endval - startval) / float(cnt)
                for i in range(cnt):
                    values.append(startval + i * dx)
            break
    return values


def get_colors(prod):
    """Do."""
    ramp = np.zeros((256, 3), np.uint8)
    data = np.zeros((30, 256), np.uint8)
    with open(f"gempak/tables/luts/iem_{prod}.tbl", encoding="ascii") as fh:
        for i, line in enumerate(fh):
            tokens = line.split()
            ramp[i, 0] = int(tokens[0])
            ramp[i, 1] = int(tokens[1])
            ramp[i, 2] = int(tokens[2])
            data[0:15, i : i + 1] = i
    return data, ramp


def main(argv):
    """Go Main Go."""
    prod = argv[1]
    values = get_values(prod)
    font = ImageFont.truetype(
        "/usr/share/fonts/liberation-mono/LiberationMono-Regular.ttf",
        10,
    )
    data, ramp = get_colors(prod.lower())

    png = Image.fromarray(data, mode="L")
    png.putpalette(tuple(ramp.ravel()))
    draw = ImageDraw.Draw(png)

    for i, value in enumerate(values[1:], start=1):
        x = i
        txt = f"{value:.02f}"
        if txt.find(".00") == -1 or value == 0:
            continue
        txt = f"{value:.0f}"
        if txt in ["15"]:
            continue
        print(txt, x)
        (w, _h) = font.getsize(txt)
        draw.line([x, 17, x, 10], fill=255)
        draw.text((x - (w / 2), 18), txt, fill=255, font=font)

    draw.text((0, 17), "inch", fill=255, font=font)

    png.save(f"{prod}.png")


if __name__ == "__main__":
    main(sys.argv)
