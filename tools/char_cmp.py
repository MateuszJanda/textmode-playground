#!/usr/bin/env python3

# Author: Mateusz Janda <mateusz janda at gmail com>
# Site: github.com/MateuszJanda/textmode-playground
# Ad maiorem Dei gloriam


from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import typing as t
import string
import itertools


def main() -> None:
    gly = GlyphShape("DejaVuSansMono", 128, 256, 256)
    print(f"Font area: {gly.get_area()}")

    gly.distance("x", "X")  # Ok
    gly.distance("a", "Z")  # Error

    # compare_chars(string.printable, string.printable)
    # compare_chars(string.ascii_letters)


def is_wide_char(font_name: str, ch: str) -> bool:
    """
    Check if character for given font is wider than standard one.
    """
    font_size = 128
    img_width = 256
    img_height = 256

    # Standard area of monospace font
    standard_gly = GlyphShape("DejaVuSansMono", font_size, img_width, img_height)
    x1, _, x2, _ = standard_gly.get_area()
    mono_width = x2 - x1 + 1

    gly = GlyphShape(font_name, font_size, img_width, img_height)
    return gly.is_wide(ch, mono_width)


def compare_chars(ch_set: str) -> None:
    """
    Compare characters similarities between two sets.
    """
    gly = GlyphShape("DejaVuSansMono", 360, 256, 512)
    print(f"Font area (x1, y1, x2, y2): {gly.get_area()}")

    count = 0
    count_fail = 0
    for ch1, ch2 in itertools.combinations(ch_set, 2):
        count += 1
        try:
            dist = gly.distance(ch1, ch2)
            # print(f"{ch1} <-> {ch2}: {dist}")
        except:
            # print(f"{ch1} <-> {ch2}: Error")
            count_fail += 1

    print(
        f"All cases: {count}, failed: {count_fail}, success rate: {((count - count_fail) / count) * 100:.2f}%"
    )


class GlyphShape:
    """
    Information about glyph shape.
    """

    def __init__(
        self,
        font_name: str,
        font_size: int,
        img_width: int,
        img_height: int,
    ) -> None:
        self._font = ImageFont.truetype(font_name, size=font_size)
        self._img_width = img_width
        self._img_height = img_height
        self._start_x = 14
        self._start_y = 14

        assert self._img_width > self._start_x
        assert self._img_height > self._start_y

    def _create_img(self, ch: str) -> "PIL.Image.Image":
        """
        Draw character glyph.
        """
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

    def get_area(self) -> t.Tuple[int, int, int, int]:
        """
        Estimate area size, that could be occupied by glyph. █ character is used as in theory
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

    def is_wide(self, ch: str, mono_width: int) -> bool:
        """
        Check if glyph is wider than standard one.
        """
        assert self._img_width > mono_width + self._start_x

        img = self._create_img(ch)
        # img.save("wide.png")
        img_arr = np.array(img)

        # Select non zero columns
        nonzero_columns = np.nonzero(np.any(img_arr != 0, axis=0))[0]
        # Check if any pixel is out of standard area
        for col in nonzero_columns:
            if col > mono_width + self._start_x:
                return True

        return False

    def is_supported(self, ch: str) -> bool:
        """
        Check if character is supported by configured font.
        """

    def distance(self, ch1: str, ch2: str) -> float:
        """
        Calculate distance between two characters glyphs.
        """
        img_arr1 = np.array(self._create_img(ch1))
        img_arr2 = np.array(self._create_img(ch2))
        contours1, _ = cv2.findContours(
            img_arr1, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_KCOS
        )
        contours2, _ = cv2.findContours(
            img_arr2, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_KCOS
        )
        self._save_with_contours(ch1, img_arr1, contours1)

        scd = cv2.createShapeContextDistanceExtractor()
        dist = scd.computeDistance(contours1[0], contours2[0])
        return dist

    def _save_with_contours(
        self, file_name: str, img_arr: np.ndarray, contours: t.Tuple
    ) -> None:
        """
        Draw counters and save image. For debug only.
        """
        img_rgb = cv2.cvtColor(img_arr, cv2.COLOR_GRAY2RGB)
        cv2.drawContours(
            img_rgb, contours, contourIdx=-1, color=(0, 0, 255), thickness=2
        )
        cv2.imwrite(f"{file_name}.png", img_rgb)


if __name__ == "__main__":
    main()
