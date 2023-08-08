#!/usr/bin/env python3

# Author: Mateusz Janda <mateusz janda at gmail com>
# Site: github.com/MateuszJanda/textmode-playground
# Ad maiorem Dei gloriam

import cv2
import numpy as np
import numpy.typing as npt


BLOCK_WIDTH = 8
BLOCK_HEIGHT = BLOCK_WIDTH


def main():
    file_name = "predator2.jpg"
    input_arr = read_img_in_grayscale(file_name)
    print(f"Image resolution: {input_arr.shape[1]}x{input_arr.shape[0]}")

    input_arr = trim_image(input_arr)
    print(f"Trim image to resolution: {input_arr.shape[1]}x{input_arr.shape[0]}")

    mean_arr = mean_values_array(input_arr)
    print(f"Output resolution: {mean_arr.shape[1]}x{mean_arr.shape[0]}")

    line = ""
    for row in range(0, mean_arr.shape[0], 2):
        for col in range(0, mean_arr.shape[1]):
            bg_color = int(mean_arr[row, col])
            fg_color = int(mean_arr[row + 1, col])
            line += f"\\e[38;2;{bg_color};{bg_color};{bg_color}m\\e[48;2;{fg_color};{fg_color};{fg_color}m▄"
        line += "\\e[m\\n"
    print(line)


def read_img_in_grayscale(path: str):
    """Get input image (gray scale) as numpy array."""
    return cv2.imread(path, cv2.IMREAD_GRAYSCALE)


def trim_image(input_arr: npt.ArrayLike) -> np.ndarray:
    """Trim image."""
    if (input_arr.shape[0] // BLOCK_HEIGHT) % 2 == 0:
        trim_height = (input_arr.shape[0] // BLOCK_HEIGHT) * BLOCK_HEIGHT
    else:
        trim_height = (
            (input_arr.shape[0] - BLOCK_HEIGHT) // BLOCK_HEIGHT
        ) * BLOCK_HEIGHT

    if (input_arr.shape[1] // BLOCK_WIDTH) % 2 == 0:
        trim_width = (input_arr.shape[1] // BLOCK_WIDTH) * BLOCK_WIDTH
    else:
        trim_width = ((input_arr.shape[1] - BLOCK_WIDTH) // BLOCK_WIDTH) * BLOCK_WIDTH

    return input_arr[:trim_height, :trim_width]


def mean_values_array(input_arr: npt.ArrayLike) -> np.ndarray:
    """Small array with mean values."""
    mean_height = input_arr.shape[0] // BLOCK_HEIGHT
    mean_width = input_arr.shape[1] // BLOCK_WIDTH
    return (
        input_arr.reshape([mean_height, BLOCK_HEIGHT, mean_width, BLOCK_WIDTH])
        .mean(3)
        .mean(1)
    )


if __name__ == "__main__":
    main()
