#!/usr/bin/env python3

# Author: Mateusz Janda <mateusz janda at gmail com>
# Site: github.com/MateuszJanda/textmode-playground
# Ad maiorem Dei gloriam

import cv2
import numpy as np


BLOCK_WIDTH = 2
BLOCK_HEIGHT = 2

def main():
    file_name = ""
    input_arr = read_img_in_grayscale(file_name)

    height = (input_arr.shape[0] // BLOCK_HEIGHT) * BLOCK_HEIGHT
    width = (input_arr.shape[1] // BLOCK_WIDTH) * BLOCK_WIDTH

    # Truncate rows and columns
    input_arr = input_arr[:height, :width]

    small_arr = input_arr.reshape([BLOCK_HEIGHT, input_arr.shape[0]//BLOCK_HEIGHT, BLOCK_WIDTH, input_arr.shape[1]//BLOCK_WIDTH]).mean(3).mean(1)

    for row in small_arr:
        for pixel in row:
            u = 50
            d = 150
            f"\033[38;2;{u};{u};{u}m\033[48;2;{d};{d};{d}m▄"


def read_img_in_grayscale(path):
    """Get input image (gray scale) as numpy array."""
    return cv2.imread(path, cv2.IMREAD_GRAYSCALE)


if __name__ == "__main__":
    main()
