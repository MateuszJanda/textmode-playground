#!/usr/bin/env python3

# Author: Mateusz Janda <mateusz janda at gmail com>
# Site: github.com/MateuszJanda/textmode-playground
# Ad maiorem Dei gloriam

import cv2
import numpy as np


def main():
    input_arr = get_input_array(args.file)

def get_input_array(path):
    """
    Get input image (gray scale) as numpy array.

    In ImageMagic this could look like this:
    convert input.png  -fx 'intensity/8' output.png
    """
    gray_img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    return gray_img

if __name__ == "__main__":
    main()
