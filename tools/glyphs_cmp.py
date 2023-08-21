#!/usr/bin/env python3

# Author: Mateusz Janda <mateusz janda at gmail com>
# Site: github.com/MateuszJanda/textmode-playground
# Ad maiorem Dei gloriam


import csv
import itertools
import random
import string
import typing as t
from collections import defaultdict

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm


def main() -> None:
    gly = GlyphShape("DejaVuSansMono", 128, 256, 256)
    print(f"Font area (x1, y1, x2, y2): {gly.get_area()}")

    # print(np.array(a), np.array(b))
    # gly.distance("x", "X")  # Ok
    # gly.distance("a", "Z")  # Error
    # gly.distance("i", "I")  # Error

    # compare_chars(string.printable)
    # compare_chars(string.ascii_letters)
    compare_chars(string.digits)


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
    gly = GlyphShape("DejaVuSansMono", 64, 128, 128)
    print(f"Font area (x1, y1, x2, y2): {gly.get_area()}")

    count_fail = 0
    all_pairs = list(itertools.combinations(ch_set, 2))
    distances = defaultdict(dict)
    for ch1, ch2 in tqdm(all_pairs):
        try:
            dist = gly.distance(ch1, ch2)
            distances[ch1][ch2] = dist
            distances[ch2][ch1] = dist
            # print(f"{ch1} <-> {ch2}: {dist}")
        except:
            distances[ch1][ch2] = -1
            distances[ch2][ch1] = -1
            # print(f"{ch1} <-> {ch2}: Error")
            count_fail += 1

    for ch in ch_set:
        distances[ch][ch] = 0

    export_distances(distances)

    print(
        f"All cases: {len(all_pairs)}, "
        f"failed: {count_fail}, "
        f"success rate: {((len(all_pairs) - count_fail) / len(all_pairs)) * 100:.2f}%"
    )


def export_distances(distances: t.Dict, file_name: str = "distances") -> None:
    """
    Export shape distances to .csv.
    """
    with open(f"{file_name}.csv", "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        # Write columns
        writer.writerow([f"0x{ord(ch):04x}" for ch in sorted(distances.keys())])
        # Write values
        for ch1 in sorted(distances.keys()):
            writer.writerow(
                [f"{distances[ch1][ch2]:.4f}" for ch2 in sorted(distances.keys())]
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
        img = self._create_img("█")
        # img.save("area.png")
        img_arr = np.array(img)

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
        contours1, _ = cv2.findContours(img_arr1, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        contours2, _ = cv2.findContours(img_arr2, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        simple_contour1 = self._simple_contour(contours1)
        simple_contour2 = self._simple_contour(contours2)
        # self._save_with_contours(ch1, img_arr1, simple_contour1)
        # self._save_with_contours(ch2, img_arr2, simple_contour2)

        scd = cv2.createShapeContextDistanceExtractor()
        dist = scd.computeDistance(simple_contour1, simple_contour2)
        return dist

    def _simple_contour(self, contours: t.Tuple, n: int = 300) -> np.ndarray:
        """
        Create simple contour.

        https://docs.opencv.org/4.8.0/d0/d38/modules_2shape_2samples_2shape_example_8cpp-example.html
        """
        tmp_contours = []
        for border in range(len(contours)):
            tmp_contours.extend(contours[border])

        # In case actual number of points is less than n, add element from the beginning
        for idx in itertools.cycle(range(len(tmp_contours))):
            if len(tmp_contours) >= n:
                break
            tmp_contours.append(tmp_contours[idx])

        # Uniformly sampling
        random.shuffle(tmp_contours)
        out_contours = [tmp_contours[idx] for idx in range(n)]
        return np.array(out_contours)

    def _save_with_contours(
        self, file_name: str, img_arr: np.ndarray, contours: t.List
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
