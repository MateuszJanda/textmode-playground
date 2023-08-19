#!/usr/bin/env python3

# Author: Mateusz Janda <mateusz janda at gmail com>
# Site: github.com/MateuszJanda/textmode-playground
# Ad maiorem Dei gloriam


from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import typing as t
import string


def main() -> None:
    cmp = CharComparator("DejaVuSansMono", 128, 256, 256)

    print(f"Font area: {cmp.font_area()}")
    _, _, _, y2 = cmp.font_area()
    print(f"Is wide: {cmp.is_wide_glyph('ね', y2)}")  # Incorrect

    # cmp.distance("x", "X")  # Ok
    # cmp.distance("a", "X")  # Error


def compare_characters():
    cmp = CharComparator("DejaVuSansMono", 128, 256, 256)

    count = 0
    count_fail = 0
    for ch1 in string.printable:
        for ch2 in string.printable:
            count += 1
            try:
                print(f"{ch1} <-> {ch2}: {cmp.distance(ch1, ch2)}")
            except:
                count_fail += 1

    print(
        f"All cases: {count}, failed: {count_fail}, success rate: {(count - count_fail)/count}"
    )


class CharComparator:
    """Compare characters similarities."""

    def __init__(
        self,
        font_name: str,
        font_size: int = 22,
        img_width: int = 32,
        img_height: int = 32,
    ) -> None:
        self._font = ImageFont.truetype(font_name, size=font_size)
        self._img_width = img_width
        self._img_height = img_height
        self._start_x = 4
        self._start_y = 4

        assert self._img_width > self._start_x
        assert self._img_height > self._start_y

    def _create_img(self, ch: str) -> "PIL.Image.Image":
        """Draw character glyph."""
        img = Image.new("L", color=0, size=(self._img_width, self._img_height))
        draw = ImageDraw.Draw(img)
        draw.text(
            xy=(self._start_x, self._start_y),
            text=ch,
            fill=255,
            font=self._font,
            spacing=0,
        )
        return img

    def font_area(self) -> t.Tuple[int, int, int, int]:
        """
        Estimate font area size, that could be occupied by glyph. █ character is used as in theory
        should occupy all available space.
        """
        img_arr = np.array(self._create_img("█"))

        # Top-left x
        x1 = None
        for col in range(0, self._img_width):
            if img_arr[self._start_y + 1, col] != 0:
                x1 = col
                break

        # Top-left y
        y1 = None
        for row in range(0, self._img_height):
            if img_arr[row, self._start_x + 1] != 0:
                y1 = row
                break

        # Top-right x
        x2 = None
        for col in range(self._img_width - 1, -1, -1):
            if img_arr[self._start_y + 1, col] != 0:
                x2 = col
                break

        # Bottom-left y
        y2 = None
        for row in range(self._img_height - 1, -1, -1):
            if img_arr[row, self._start_x + 1] != 0:
                y2 = row
                break

        return x1, y1, x2, y2

    def is_wide_glyph(self, ch: str, mono_width: int) -> bool:
        """Check if glyph occupies more area than standard character."""
        assert self._img_width > mono_width

        img = self._create_img(ch)
        # img.save("wide.png")
        img_arr = np.array(img)

        # Select non zero columns
        nonzero_columns = np.nonzero(np.any(img_arr != 0, axis=0))[0]

        for col in nonzero_columns:
            if col > mono_width:
                return True

        return False

    def is_char_supported(self) -> bool:
        """Check if character is supported by configured font."""

    def distance(self, ch1: str, ch2: str) -> float:
        """Calculate distance between two characters glyphs."""
        img_arr1 = np.array(self._create_img(ch1))
        img_arr2 = np.array(self._create_img(ch2))
        con1, _ = cv2.findContours(img_arr1, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_KCOS)
        con2, _ = cv2.findContours(img_arr2, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_KCOS)
        scd = cv2.createShapeContextDistanceExtractor()
        dist = scd.computeDistance(con1[0], con2[0])
        return dist


if __name__ == "__main__":
    main()
