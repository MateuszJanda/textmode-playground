#!/usr/bin/env python3

# Author: Mateusz Janda <mateusz janda at gmail com>
# Site: github.com/MateuszJanda/textmode-playground
# Ad maiorem Dei gloriam


from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np


def main() -> None:
    dist("x", "X")  # Ok
    dist("a", "X")  # Error


def create_img(ch: str, pos_x: int = 3, pos_y: int = 2) -> np.ndarray:
    IMG_SHAPE = (17, 14)
    img = Image.new("L", color=0, size=(IMG_SHAPE[1], IMG_SHAPE[0]))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("DejaVuSansMono", size=12)
    draw.text(xy=(pos_x, pos_y), text=ch, fill=255, font=font, spacing=0)

    img.save(f"{ch}.png")
    return np.array(img)


def dist(ch1: str, ch2: str) -> None:
    img1 = create_img(ch1)
    img2 = create_img(ch2)
    con1, _ = cv2.findContours(img1, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_KCOS)
    con2, _ = cv2.findContours(img2, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_KCOS)
    hd = cv2.createHausdorffDistanceExtractor()
    sd = cv2.createShapeContextDistanceExtractor()
    print(f"{ch1} <-> {ch2}: hd {hd.computeDistance(con1[0], con2[0])}")
    print(f"{ch1} <-> {ch2}: sd {sd.computeDistance(con1[0], con2[0])}")


if __name__ == "__main__":
    main()
