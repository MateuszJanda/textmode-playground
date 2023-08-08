#!/usr/bin/env python3

# Author: Mateusz Janda <mateusz janda at gmail com>
# Site: github.com/MateuszJanda/textmode-playground
# Ad maiorem Dei gloriam

import cv2
import numpy as np


BLOCK_WIDTH = 8
BLOCK_HEIGHT = BLOCK_WIDTH


def main():
    file_name = "predator2.jpg"
    input_arr = read_img_in_grayscale(file_name)
    print(f"Image resolution: {input_arr.shape[1]}x{input_arr.shape[0]}")

    # Trim image
    if (input_arr.shape[0] // BLOCK_HEIGHT) % 2 == 0:
        trim_height = (input_arr.shape[0] // BLOCK_HEIGHT) * BLOCK_HEIGHT
    else:
        trim_height = ((input_arr.shape[0] - BLOCK_HEIGHT)// BLOCK_HEIGHT) * BLOCK_HEIGHT

    if (input_arr.shape[1] // BLOCK_WIDTH) % 2 == 0:
        trim_width = (input_arr.shape[1] // BLOCK_WIDTH) * BLOCK_WIDTH
    else:
        trim_width = ((input_arr.shape[1] - BLOCK_WIDTH ) // BLOCK_WIDTH) * BLOCK_WIDTH

    input_arr = input_arr[:trim_height, :trim_width]
    print(f"Trim image to resolution: {input_arr.shape[1]}x{input_arr.shape[0]}")

    # Small array with mean values
    mean_height = trim_height // BLOCK_HEIGHT
    mean_width = trim_width // BLOCK_WIDTH
    mean_arr = input_arr.reshape([mean_height, trim_height//mean_height, mean_width, trim_width//mean_height]).mean(3).mean(1)
    print(f"Output resolution: {mean_arr.shape[1]}x{mean_arr.shape[0]}")

    line = ""
    for row in range(0, mean_arr.shape[0], 2):
        for col in range(0, mean_arr.shape[1]):
            bg_color = int(mean_arr[row, col])
            fg_color = int(mean_arr[row + 1, col])
            # print(bg_color, " ")
            line += f"\\033[38;2;{bg_color};{bg_color};{bg_color}m\\033[48;2;{fg_color};{fg_color};{fg_color}m▄"
            # line += f"\033[38;2;{bg_color};{bg_color};{bg_color}m\033[48;2;{fg_color};{fg_color};{fg_color}m▄"
        line += "\\n"
    print(line)


def read_img_in_grayscale(path):
    """Get input image (gray scale) as numpy array."""
    return cv2.imread(path, cv2.IMREAD_GRAYSCALE)


if __name__ == "__main__":
    main()
