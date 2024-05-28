"""Convert a GIF to a PNG.

ImageMagick seems upset with the legacy GIF format.
"""

import click
from PIL import Image


@click.command()
@click.option("--input", "-i", help="Input GIF file", required=True)
@click.option("--output", "-o", help="Output PNG file", required=True)
def main(input, output):
    """Go Main Go."""
    with Image.open(input) as gif:
        gif.save(output)


if __name__ == "__main__":
    main()
