#!/usr/bin/env python3

# Author: Mateusz Janda <mateusz janda at gmail com>
# Site: github.com/MateuszJanda/textmode-playground
# Ad maiorem Dei gloriam

import argparse
import cv2
import numpy as np
import numpy.typing as npt


CELL_WIDTH = 2
CELL_HEIGHT = 4


class CustomFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    pass


def main():
    """
    $ echo -e `python img_to_ansi.py`
    """
    # Parse arguments
    args = parse_args()

    # Read image and convert to grayscale
    input_arr = cv2.imread(args.input_path, cv2.IMREAD_GRAYSCALE)

    # Trim image. Resolution should be a multiple of the block size
    input_arr = trim_image(input_arr, args.block_size)

    # Reduce image size. Values are averages of their neighbors
    mean_arr = mean_values_array(input_arr, args.block_size)

    # Create braille strings
    pixel_arr = np.where(mean_arr > args.threshold, 1, 0)
    line = ""
    for row in range(0, pixel_arr.shape[0], CELL_HEIGHT):
        for col in range(0, pixel_arr.shape[1], CELL_WIDTH):
            # Empty braille
            ch_code = 0x2800
            # https://en.wikipedia.org/wiki/Braille_Patterns
            ch_code |= 0x00 if pixel_arr[row + 0, col + 0] else 0x01
            ch_code |= 0x00 if pixel_arr[row + 1, col + 0] else 0x02
            ch_code |= 0x00 if pixel_arr[row + 2, col + 0] else 0x04
            ch_code |= 0x00 if pixel_arr[row + 3, col + 0] else 0x40

            ch_code |= 0x00 if pixel_arr[row + 0, col + 1] else 0x08
            ch_code |= 0x00 if pixel_arr[row + 1, col + 1] else 0x10
            ch_code |= 0x00 if pixel_arr[row + 2, col + 1] else 0x20
            ch_code |= 0x00 if pixel_arr[row + 3, col + 1] else 0x80
            line += f"{chr(ch_code)}"
        line += "\n"
    print(line)


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Convert RGB image to ANSI\n"
        "\n"
        "Example:\n"
        "$ echo -e `python img_to_ansi.py --block-size 8 --input-path cat.jpg`\n",
        usage="Please try to use -h, --help for more information's",
        epilog=" \n",
        formatter_class=CustomFormatter,
    )
    parser.add_argument(
        "-i", "--input-path", required=True, action="store", help="Path to input file."
    )
    parser.add_argument(
        "-t",
        "--threshold",
        required=True,
        action="store",
        type=int,
        help="Threshold for grayscale image.",
    )
    parser.add_argument(
        "-b",
        "--block-size",
        required=True,
        action="store",
        type=int,
        help="Size of block (pixels) that will be converted to ANSI half block.",
    )
    return parser.parse_args()


def trim_image(input_arr: npt.ArrayLike, block_size: int) -> np.ndarray:
    """Trim image."""
    # Least common multiple (.pl NWW) for height
    height = np.lcm(block_size, CELL_HEIGHT)
    if (input_arr.shape[0] // height) % 2 == 0:
        trim_height = (input_arr.shape[0] // height) * height
    else:
        trim_height = ((input_arr.shape[0] - height) // height) * height

    # Least common multiple (.pl NWW) for width
    width = np.lcm(block_size, CELL_WIDTH)
    if (input_arr.shape[1] // width) % 2 == 0:
        trim_width = (input_arr.shape[1] // width) * width
    else:
        trim_width = ((input_arr.shape[1] - width) // width) * width

    return input_arr[:trim_height, :trim_width]


def mean_values_array(input_arr: npt.ArrayLike, block_size: int) -> np.ndarray:
    """Array with reduced shape and mean values of it neighbors."""
    mean_height = input_arr.shape[0] // block_size
    mean_width = input_arr.shape[1] // block_size
    return (
        input_arr.reshape([mean_height, block_size, mean_width, block_size])
        .mean(axis=3)
        .mean(axis=1)
        .astype(int)
    )


if __name__ == "__main__":
    main()
