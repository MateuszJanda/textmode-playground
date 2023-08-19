#!/usr/bin/env python3

# Author: Mateusz Janda <mateusz janda at gmail com>
# Site: github.com/MateuszJanda/textmode-playground
# Ad maiorem Dei gloriam


from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import typing as t


def main() -> None:
    cmp = CharComparator("DejaVuSansMono", 12, 48, 48)
    print(cmp.font_area())
    # cmp.dist("x", "X")  # Ok
    # cmp.dist("a", "X")  # Error


class CharComparator:
    """Compare characters similarities."""

    def __init__(
        self,
        font_name: str,
        font_size: int = 12,
        img_width: int = 14,
        img_height: int = 17,
    ) -> None:
        self._font = ImageFont.truetype(font_name, size=font_size)
        self._img_width = img_width
        self._img_height = img_height

    def font_area(self) -> t.Tuple[int, int, int, int]:
        """
        Estimate font area size, that could be occupied by glyph. █ character is used as in theory
        should occupy all available space.
        """
        start_x = 4
        start_y = 4
        assert self._img_width > start_x
        assert self._img_height > start_y

        img = Image.new("L", color=0, size=(self._img_width, self._img_height))
        draw = ImageDraw.Draw(img)
        draw.text(xy=(start_x, start_y), text="█", fill=255, font=self._font, spacing=0)
        img = np.array(img)

        # Top-left x
        x1 = None
        for col in range(0, self._img_width):
            if img[start_y + 1, col] != 0:
                x1 = col
                break

        # Top-left y
        y1 = None
        for row in range(0, self._img_height):
            if img[row, start_x + 1] != 0:
                y1 = row
                break

        # Top-right x
        x2 = None
        for col in range(self._img_width - 1, -1, -1):
            if img[start_y + 1, col] != 0:
                x2 = col
                break

        # Bottom-left y
        y2 = None
        for row in range(self._img_height - 1, -1, -1):
            if img[row, start_x + 1] != 0:
                y2 = row
                break

        return x1, y1, x2, y2

    def _create_img(self, ch: str, start_x: int = 3, start_y: int = 3) -> np.ndarray:
        """Draw character glyph."""
        img = Image.new("L", color=0, size=(self._img_width, self._im_height))
        draw = ImageDraw.Draw(img)
        draw.text(xy=(start_x, start_y), text=ch, fill=255, font=self._font, spacing=0)
        # img.save(f"{ch}.png")
        return np.array(img)

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
