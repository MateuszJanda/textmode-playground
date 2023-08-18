#!/usr/bin/env python3

# Author: Mateusz Janda <mateusz janda at gmail com>
# Site: github.com/MateuszJanda/textmode-playground
# Ad maiorem Dei gloriam

import argparse
import cv2
import numpy as np
import numpy.typing as npt


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

    # Read image as BGR (not RGB!)
    input_arr = cv2.imread(args.input_path)

    # Trim image. Resolution should be a multiple of the block size
    input_arr = trim_image(input_arr, args.block_size)

    # Reduce image size. Values are averages of their neighbors
    mean_arr = mean_values_array(input_arr, args.block_size)

    # Create ANSI string
    line = ""
    for row in range(0, mean_arr.shape[0], 2):
        for col in range(0, mean_arr.shape[1]):
            bg_r = mean_arr[row, col, 2]
            bg_g = mean_arr[row, col, 1]
            bg_b = mean_arr[row, col, 0]
            fg_r = mean_arr[row + 1, col, 2]
            fg_g = mean_arr[row + 1, col, 1]
            fg_b = mean_arr[row + 1, col, 0]
            line += f"\\e[38;2;{bg_r};{bg_g};{bg_b}m\\e[48;2;{fg_r};{fg_g};{fg_b}m▄"
        line += "\\e[m\\n"
    print(line)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
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
    if (input_arr.shape[0] // block_size) % 2 == 0:
        trim_height = (input_arr.shape[0] // block_size) * block_size
    else:
        trim_height = ((input_arr.shape[0] - block_size) // block_size) * block_size

    if (input_arr.shape[1] // block_size) % 2 == 0:
        trim_width = (input_arr.shape[1] // block_size) * block_size
    else:
        trim_width = ((input_arr.shape[1] - block_size) // block_size) * block_size

    return input_arr[:trim_height, :trim_width]


def mean_values_array(input_arr: npt.ArrayLike, block_size: int) -> np.ndarray:
    """Array with reduced shape and mean values of their neighbors."""
    mean_height = input_arr.shape[0] // block_size
    mean_width = input_arr.shape[1] // block_size
    return (
        input_arr.reshape([mean_height, block_size, mean_width, block_size, 3])
        .mean(axis=3)
        .mean(axis=1)
        .astype(int)
    )


if __name__ == "__main__":
    main()
