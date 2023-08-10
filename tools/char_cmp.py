#!/usr/bin/env python3

# Author: Mateusz Janda <mateusz janda at gmail com>
# Site: github.com/MateuszJanda/textmode-playground
# Ad maiorem Dei gloriam


from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

IMG_HEIGHT = 17
IMG_WIDTH = 14


def main() -> None:
    cmp = CharComparator()
    cmp.dist("x", "X")  # Ok
    cmp.dist("a", "X")  # Error


class CharComparator:
    def __init__(self) -> None:
        self.font = ImageFont.truetype("DejaVuSansMono", size=12)

    def _create_img(self, ch: str, start_x: int = 3, start_y: int = 3) -> np.ndarray:
        """Draw character glyph."""
        img = Image.new("L", color=0, size=(IMG_WIDTH, IMG_HEIGHT))
        draw = ImageDraw.Draw(img)
        draw.text(xy=(start_x, start_y), text=ch, fill=255, font=self.font, spacing=0)
        # img.save(f"{ch}.png")
        # return np.array(img)
        return img

    def dist(self, ch1: str, ch2: str) -> None:
        """Calculate distance between two characters glyph."""
        img1 = self._create_img(ch1)
        img2 = self._create_img(ch2)
        con1, _ = cv2.findContours(img1, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_KCOS)
        con2, _ = cv2.findContours(img2, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_KCOS)
        hd = cv2.createHausdorffDistanceExtractor()
        sd = cv2.createShapeContextDistanceExtractor()
        print(f"HD: {ch1} <-> {ch2} == {hd.computeDistance(con1[0], con2[0])}")
        print(f"SD: {ch1} <-> {ch2} == {sd.computeDistance(con1[0], con2[0])}")


if __name__ == "__main__":
    main()
