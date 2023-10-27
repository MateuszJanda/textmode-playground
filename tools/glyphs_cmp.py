#!/usr/bin/env python3

# Author: Mateusz Janda <mateusz janda at gmail com>
# Site: github.com/MateuszJanda/textmode-playground
# Ad maiorem Dei gloriam


import csv
import itertools
import random
import string
import subprocess
import typing as t
from collections import defaultdict

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm

r"""
Print glyph (⢧):
$ echo -e '\U28a7'

Print all (:) fonts supporting given character (file path, family and fontformat
(e.g. TrueType)):
$ fc-list :charset=0x28a7 file family fontformat

Print font ranges supported by given font:
$ fc-query /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf --format='%{charset}\n'
"""


def main() -> None:
    gly_cmp = GlyphCmp()
    gly = GlyphDrawer(
        font_name="DejaVuSansMono",
        font_path="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        font_size=350,
        img_width=256,
        img_height=350,
    )
    print(f"Font area (x1, y1, x2, y2): {gly.get_area()}")
    # print(gly.is_supported("a"))
    # print(gly.is_supported("⢧"))
    print_distance = lambda ch1, ch2: print(
        f"Dst {ch1} <-> {ch2}: {gly_cmp.distance(ch1, gly, ch2, gly)}"
    )
    # print_distance("x", "x")
    # print_distance("x", "X")
    # print_distance(" ", "x")
    # print_distance("x", "q")
    # print_distance(".", ",")
    # print_distance(".", "`")
    # print_distance("1", "|")
    # print_distance("1", "l")
    # print_distance("1", "-")

    gly = GlyphDrawer(
        font_name="DejaVuSans",
        font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        font_size=200,
        img_width=300,
        img_height=310,
    )
    # print(gly.is_supported("a"))
    # print(gly.is_supported("⢧"))

    # print_distance("⢧", "⢧")
    # print_distance("⢧", "⢧")
    # print_distance("⢷", "⢧")
    # print_distance("⢧", "⢷")
    # print_distance("⢧", "⢷")
    # print_distance("⢧", "⢷")
    # print_distance("⢧", "⢷")
    # print_distance("i", "⢷")
    # print_distance("X", "x")
    # print_distance("X", "X")
    print_distance("0", "o")
    print_distance("0", "o")
    print_distance("0", "o")
    print_distance("o", "0")
    print_distance("o", "0")
    print_distance("o", "0")
    # print_distance("X", "⢷")
    # print_distance("/", "/")
    # print_distance("/", "/")
    # print_distance("/", "/")
    # print_distance("/", "|")
    # print_distance("/", "|")
    # print_distance("/", "|")
    # print_distance("/", "\\")
    # print_distance("/", "\\")
    # print_distance("/", "\\")
    # compare_chars(string.printable)
    # compare_chars(string.ascii_letters)
    # compare_chars(string.digits)

    # distance_of_standardized_subset()


def distance_of_standardized_subset() -> None:
    """
    https://en.wikipedia.org/wiki/Unicode#Standardized_subsets
    """

    # Basic Latin (00–7F)
    unicode_subset = []
    unicode_subset += [chr(code) for code in range(0x0020, 0x007F + 1)]
    # Latin-1 Supplement (80–FF)
    unicode_subset += [chr(code) for code in range(0x0080, 0x00FF + 1)]
    # Latin Extended-A (00–7F)
    unicode_subset += [chr(code) for code in range(0x0100, 0x017F + 1)]
    # Latin Extended-B (80–FF ...)
    unicode_subset += [chr(code) for code in range(0x0180, 0x01FF + 1)]
    # Latin Extended-B (... 00–4F)
    unicode_subset += [chr(code) for code in range(0x0200, 0x024F + 1)]
    # IPA Extensions (50–AF)
    unicode_subset += [chr(code) for code in range(0x0250, 0x02AF + 1)]
    # Spacing Modifier Letters (B0–FF)
    unicode_subset += [chr(code) for code in range(0x02B0, 0x02FF + 1)]
    # Greek (70–FF)
    unicode_subset += [chr(code) for code in range(0x0370, 0x03FF + 1)]
    # Cyrillic (00–FF)
    unicode_subset += [chr(code) for code in range(0x0400, 0x04FF + 1)]
    # Latin Extended Additional (00–FF)
    unicode_subset += [chr(code) for code in range(0x1E00, 0x1EFF + 1)]
    # Greek Extended (00–FF)
    unicode_subset += [chr(code) for code in range(0x1F00, 0x1FFF + 1)]
    # General Punctuation (00–6F)
    unicode_subset += [chr(code) for code in range(0x2000, 0x206F + 1)]
    # Superscripts and Subscripts (70–9F)
    unicode_subset += [chr(code) for code in range(0x2070, 0x209F + 1)]
    # Currency Symbols (A0–CF)
    unicode_subset += [chr(code) for code in range(0x20A0, 0x20CF + 1)]
    # Letterlike Symbols (00–4F)
    unicode_subset += [chr(code) for code in range(0x2100, 0x214F + 1)]
    # Number Forms (50–8F)
    unicode_subset += [chr(code) for code in range(0x2150, 0x218F + 1)]
    # Arrows (90–FF)
    unicode_subset += [chr(code) for code in range(0x2190, 0x21FF + 1)]
    # Mathematical Operators (00–FF)
    unicode_subset += [chr(code) for code in range(0x2200, 0x22FF + 1)]
    # Miscellaneous Technical (00–FF)
    # unicode_subset += [chr(code) for code in range(0x2300, 0x23FF + 1)]
    # Box Drawing (00–7F)
    unicode_subset += [chr(code) for code in range(0x2500, 0x257F + 1)]
    # Block Elements (80–9F)
    unicode_subset += [chr(code) for code in range(0x2580, 0x259F + 1)]
    # Geometric Shapes (A0–FF)
    unicode_subset += [chr(code) for code in range(0x25A0, 0x25FF + 1)]
    # Miscellaneous Symbols (00–FF)
    # unicode_subset += [chr(code) for code in range(0x2600, 0x26FF + 1)]
    # Private Use Area (00–FF ...)
    # unicode_subset += [chr(code) for code in range(0xF000, 0xF0FF + 1)]
    # Alphabetic Presentation Forms (00–4F)
    unicode_subset += [chr(code) for code in range(0xFB00, 0xFB4F + 1)]
    # Specials
    # unicode_subset += [0xFFFD]

    # compare_chars(unicode_subset)


def is_wide_char(font_name: str, font_path: str, ch: str) -> bool:
    """
    Check if character for given font is wider than standard one.
    """
    font_size = 350
    img_width = 256
    img_height = 350

    # Standard area of monospace font
    standard_gly = GlyphDrawer(
        font_name="DejaVuSansMono",
        font_path="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        font_size=font_size,
        img_width=img_width,
        img_height=img_height,
    )
    x1, _, x2, _ = standard_gly.get_area()
    mono_width = x2 - x1 + 1

    gly = GlyphDrawer(font_name, font_path, font_size, img_width, img_height)
    return gly.is_wide(ch, mono_width)


def compare_chars(ch_set: str) -> None:
    """
    Compare characters similarities between two sets.
    """
    gly = GlyphDrawer(
        font_name="DejaVuSansMono",
        font_path="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        font_size=350,
        img_width=256,
        img_height=350,
    )
    print(f"Font area (x1, y1, x2, y2): {gly.get_area()}")

    gly_cmp = GlyphCmp()
    count_fail = 0
    all_pairs = list(itertools.combinations(ch_set, 2))
    distances = defaultdict(dict)
    for ch1, ch2 in tqdm(all_pairs):
        try:
            dist = gly_cmp.distance(ch1, gly, ch2, gly)
            distances[ch1][ch2] = dist
            distances[ch2][ch1] = dist
        except:
            distances[ch1][ch2] = -1
            distances[ch2][ch1] = -1
            print(f"{ch1} <-> {ch2}: Error")
            count_fail += 1

    for ch in ch_set:
        distances[ch][ch] = 0

    export_distances_to_csv(distances)

    print(
        f"All cases: {len(all_pairs)}, "
        f"failed: {count_fail}, "
        f"success rate: {((len(all_pairs) - count_fail) / len(all_pairs)) * 100:.2f}%"
    )


def export_distances_to_csv(distances: t.Dict, file_name: str = "distances") -> None:
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


class GlyphDrawer:
    """
    Glyph drawer by specified font.
    """

    def __init__(
        self,
        font_name: str,
        font_path: str,
        font_size: int,
        img_width: int,
        img_height: int,
    ) -> None:
        self._font = ImageFont.truetype(font_name, size=font_size)
        self._font_path = font_path
        self._img_width = img_width
        self._img_height = img_height
        self._start_x = 64
        self._start_y = 24

        assert self._img_width > self._start_x
        assert self._img_height > self._start_y

        self._charset = self._extract_charset()

    def _extract_charset(self) -> t.List:
        """
        Extract charset supported by font, using fc-query.
        """
        output = subprocess.run(
            ["fc-query", f"{self._font_path}", r"--format=%{charset}\n"],
            stdout=subprocess.PIPE,
        )

        result = []
        for line in output.stdout.decode("utf-8").strip().split("\n"):
            if not line:
                continue

            for char_range in line.split():
                if "-" in char_range:
                    first, last = char_range.split("-")
                    result.append((int(first, 16), int(last, 16)))
                else:
                    result.append((int(char_range, 16), int(char_range, 16)))

        return result

    def create_img(self, ch: str) -> np.ndarray:
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
        return np.array(img)

    def get_area(self) -> t.Tuple[int, int, int, int]:
        """
        Estimate area size, that could be occupied by glyph. █ character is used as in theory
        should occupy all available space.
        """
        img_arr = self.create_img("█")

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

        img_arr = self.create_img(ch)

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
        ch_code = ord(ch)

        for char_range in self._charset:
            if char_range[0] <= ch_code <= char_range[1]:
                return True

        return False


class GlyphCmp:
    """
    Glyphs comparator.
    """

    def distance(
        self, ch1: str, gly1: GlyphDrawer, ch2: str, gly2: GlyphDrawer
    ) -> float:
        """
        Calculate distance between two characters glyphs.
        """
        img_arr1 = gly1.create_img(ch1)
        img_arr2 = gly2.create_img(ch2)

        # Dilatate to join glyph parts
        dil_arr1 = cv2.dilate(img_arr1, cv2.getStructuringElement(cv2.MORPH_RECT, (23, 23)))
        dil_arr2 = cv2.dilate(img_arr2, cv2.getStructuringElement(cv2.MORPH_RECT, (23, 23)))

        # contours1, _ = cv2.findContours(img_arr1, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        # contours2, _ = cv2.findContours(img_arr2, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        contours1, _ = cv2.findContours(dil_arr1, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        contours2, _ = cv2.findContours(dil_arr2, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        if (len(contours1) == 0 or len(contours2) == 0):
            return 0

        contour1 = self._simple_contour(contours1)
        contour2 = self._simple_contour(contours2)

        self._save_with_contours(ch1, img_arr1, contour1)
        # self._save_with_contours(ch2, img_arr2, contour2)
        scd = cv2.createShapeContextDistanceExtractor()
        dist = scd.computeDistance(contour1, contour2)
        return dist

    def _simple_contour(
        self, contours: t.Tuple, num_of_contours: int = 300
    ) -> np.ndarray:
        """
        Create simple contour.

        https://docs.opencv.org/4.8.0/d0/d38/modules_2shape_2samples_2shape_example_8cpp-example.html
        """
        tmp_contour = []
        for contour in contours:
            tmp_contour.extend(contour)

        # In case actual number of points is less than n, add element from the beginning
        for idx in itertools.cycle(range(len(tmp_contour))):
            if len(tmp_contour) >= num_of_contours:
                break
            tmp_contour.append(tmp_contour[idx])

        # Uniformly sampling
        random.shuffle(tmp_contour)
        ret_contour = [tmp_contour[idx] for idx in range(num_of_contours)]
        return np.array(ret_contour)

    def _save_with_contours(
        self, ch: str, img_arr: np.ndarray, contours: t.List
    ) -> None:
        """
        Draw counters and save image. For debug only.
        """
        img_rgb = cv2.cvtColor(img_arr, cv2.COLOR_GRAY2RGB)
        cv2.drawContours(
            img_rgb, contours, contourIdx=-1, color=(0, 0, 255), thickness=2
        )
        cv2.imwrite(f"0x{ord(ch):04x}.png", img_rgb)


if __name__ == "__main__":
    main()
