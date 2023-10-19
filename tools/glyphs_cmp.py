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
    print(gly.is_supported("a"))
    print(gly.is_supported("⢧"))
    print_distance = lambda ch1, ch2: print(f'Dst {ch1} <-> {ch2}: {gly_cmp.distance(ch1, gly, ch2, gly)}')
    print_distance("x", "x")
    print_distance("x", "X")
    # print_distance("x", "q")
    # print_distance(".", ",")
    # print_distance(".", "`")
    # print_distance("1", "|")
    # print_distance("1", "l")
    # print_distance("1", "-")

    gly = GlyphDrawer(
        font_name="DejaVuSans",
        font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        font_size=350,
        img_width=256,
        img_height=350,
    )
    print(gly.is_supported("a"))
    print(gly.is_supported("⢧"))

    # compare_chars(string.printable)
    # compare_chars(string.ascii_letters)
    # compare_chars(string.digits)


def distance_of_standardized_subset() -> None:
    """
    https://en.wikipedia.org/wiki/Unicode#Standardized_subsets
    """
    # Basic Latin (00–7F)
    unicode_subset = [chr(code) for code in range(0x0020, 0x007F + 1)]
    # Latin-1 Supplement (80–FF)
    unicode_subset += [chr(code) for code in range(0x0080, 0x0077 + 1)]
    # Latin Extended-A (00–7F)
    unicode_subset += [chr(code) for code in range(0x0100, 0x017F + 1)]
    # Latin Extended-B (80–FF ...)
    unicode_subset += [chr(code) for code in [0x018F, 0x0192,0x01B7,0x018F]]
    unicode_subset += [chr(code) for code in range(0x01DE, 0x01EF + 1)]
    unicode_subset += [chr(code) for code in range(0x01FA, 0x01FF + 1)]
    # Latin Extended-B (... 00–4F)
    unicode_subset += [chr(code) for code in range(0x0218, 0x021B + 1)]
    unicode_subset += [chr(code) for code in range(0x021E, 0x021F + 1)]
    # IPA Extensions (50–AF)
    unicode_subset += [chr(code) for code in [0x0259, 0x027c, 0x0292]]
    # Spacing Modifier Letters (B0–FF)
    unicode_subset += [chr(code) for code in range(0x02BB, 0x02bd + 1)]
    unicode_subset += [chr(code) for code in [0x02c6, 0x02c7, 0x02c8, 0x02c9, 0x02d6, ]]
    unicode_subset += [chr(code) for code in range(0x02d8, 0x02db + 1)]
    unicode_subset += [chr(code) for code in [0x02dc, 0x02dd, 0x02df, 0x02ee, ]]
    # Greek (70–FF)
    unicode_subset += [chr(code) for code in range(0x0374, 0x0375 + 1)]
    unicode_subset += [chr(code) for code in [0x037a, 0x037e, ]]
    unicode_subset += [chr(code) for code in range(0x0384, 0x038a + 1)]
    unicode_subset += [chr(code) for code in [0x038c]]
    unicode_subset += [chr(code) for code in range(0x038e, 0x03a1 + 1)]
    unicode_subset += [chr(code) for code in range(0x03a3, 0x03c3 + 1)]
    unicode_subset += [chr(code) for code in [0x03d7]]
    unicode_subset += [chr(code) for code in range(0x03da, 0x03e1 + 1)]
    # Cyrillic (00–FF)
    unicode_subset += [chr(code) for code in range(0x0400, 0x045f + 1)]
    unicode_subset += [chr(code) for code in range(0x0490, 0x0491 + 1)]
    unicode_subset += [chr(code) for code in range(0x0492, 0x04c4 + 1)]
    unicode_subset += [chr(code) for code in range(0x04c7, 0x04c8 + 1)]
    unicode_subset += [chr(code) for code in range(0x04cb, 0x04cc + 1)]
    unicode_subset += [chr(code) for code in range(0x04d0, 0x04eb + 1)]
    unicode_subset += [chr(code) for code in range(0x04ee, 0x04f5 + 1)]
    unicode_subset += [chr(code) for code in range(0x04f8, 0x04f9 + 1)]
    # Latin Extended Additional (00–FF)
    unicode_subset += [chr(code) for code in range(0x1e02, 0x1e03 + 1)]
    unicode_subset += [chr(code) for code in range(0x1e0a, 0x1e0b + 1)]
    unicode_subset += [chr(code) for code in range(0x1e1e, 0x1e1f + 1)]
    unicode_subset += [chr(code) for code in range(0x1e40, 0x1e41 + 1)]
    unicode_subset += [chr(code) for code in range(0x1e56, 0x1e57 + 1)]
    unicode_subset += [chr(code) for code in range(0x1e60, 0x1e61 + 1)]
    unicode_subset += [chr(code) for code in range(0x1e6a, 0x1e6b + 1)]
    unicode_subset += [chr(code) for code in range(0x1e80, 0x1e85 + 1)]
    unicode_subset += [chr(code) for code in [0x1e9b]]
    unicode_subset += [chr(code) for code in range(0x1ef2, 0x1ef3 + 1)]
    # Greek Extended (00–FF)
    unicode_subset += [chr(code) for code in range(0x1f00, 0x1f15 + 1)]
    unicode_subset += [chr(code) for code in range(0x1f18, 0x1f1d + 1)]
    unicode_subset += [chr(code) for code in range(0x1f20, 0x1f45 + 1)]
    unicode_subset += [chr(code) for code in range(0x1f48, 0x1f4d + 1)]
    unicode_subset += [chr(code) for code in range(0x1f50, 0x1f57 + 1)]
    unicode_subset += [chr(code) for code in [0x1f59, 0x1f5b,0x1f5d,  ]]
    unicode_subset += [chr(code) for code in range(0x1f5f, 0x1f7d + 1)]
    unicode_subset += [chr(code) for code in range(0x1f80, 0x1fb4 + 1)]
    unicode_subset += [chr(code) for code in range(0x1f86, 0x1fc4 + 1)]
    unicode_subset += [chr(code) for code in range(0x1fc6, 0x1fd3 + 1)]
    unicode_subset += [chr(code) for code in range(0x1fd6, 0x1fdb + 1)]
    unicode_subset += [chr(code) for code in range(0x1fdd, 0x1fef + 1)]
    unicode_subset += [chr(code) for code in range(0x1ff2, 0x1ff4 + 1)]
    unicode_subset += [chr(code) for code in range(0x1ff6, 0x1ffe + 1)]
    # General Punctuation (00–6F)
    unicode_subset += [chr(code) for code in range(0x2013, 0x2014 + 1)]
    unicode_subset += [chr(code) for code in [0x2015, 0x2017]]
    unicode_subset += [chr(code) for code in range(0x2018, 0x2019 + 1)]
    unicode_subset += [chr(code) for code in range(0x201a, 0x201b + 1)]
    unicode_subset += [chr(code) for code in range(0x201c, 0x201d + 1)]
    unicode_subset += [chr(code) for code in [0x201e]]
    unicode_subset += [chr(code) for code in range(0x2020, 0x2022 + 1)]
    unicode_subset += [chr(code) for code in [0x2026, 0x2030, ]]
    unicode_subset += [chr(code) for code in range(0x2032, 0x2033 + 1)]
    unicode_subset += [chr(code) for code in range(0x2039, 0x203a + 1)]
    unicode_subset += [chr(code) for code in [0x203c, 0x203e, 0x2044, 0x204A ]]
    # Superscripts and Subscripts (70–9F)
    unicode_subset += [chr(code) for code in [0x207f, 0x2082, ]]
    # Currency Symbols (A0–CF)
    unicode_subset += [chr(code) for code in range(0x20a3, 0x20a4 + 1)]
    unicode_subset += [chr(code) for code in [0x20a7, 0x20ac, 0x20af, ]]
    # Letterlike Symbols (00–4F)
    unicode_subset += [chr(code) for code in [0x2105, 0x2113, 0x2116, 0x2122, 0x2126, 0x212e, ]]
    # Number Forms (50–8F)
    unicode_subset += [chr(code) for code in range(0x2150, 0x218f + 1)]
    # Arrows (90–FF)
    unicode_subset += [chr(code) for code in range(0x2190, 0x2193 + 1)]
    unicode_subset += [chr(code) for code in range(0x2194, 0x2195 + 1)]
    unicode_subset += [chr(code) for code in [0x21a8 ]]
    # Mathematical Operators (00–FF)
    unicode_subset += [chr(code) for code in [0x2200, 0x2202,0x2203,0x2206,   ]]
    unicode_subset += [chr(code) for code in range(0x2208, 0x2209 + 1)]
    unicode_subset += [chr(code) for code in [0x220f   ]]
    unicode_subset += [chr(code) for code in range(0x2211, 0x2212 + 1)]
    unicode_subset += [chr(code) for code in [0x2215   ]]
    unicode_subset += [chr(code) for code in range(0x2219, 0x221a + 1)]
    unicode_subset += [chr(code) for code in range(0x221e, 0x221f + 1)]
    unicode_subset += [chr(code) for code in range(0x2227, 0x2228 + 1)]
    unicode_subset += [chr(code) for code in [0x2229,0x222a,0x222b,0x2248,0x2259,       ]]
    unicode_subset += [chr(code) for code in range(0x2260, 0x2261 + 1)]
    unicode_subset += [chr(code) for code in range(0x2264, 0x2265 + 1)]
    unicode_subset += [chr(code) for code in range(0x2282, 0x2283 + 1)]
    unicode_subset += [chr(code) for code in [0x2295,0x2297,]]
    # Miscellaneous Technical (00–FF)
    unicode_subset += [chr(code) for code in [0x2302,0x230a,]]
    unicode_subset += [chr(code) for code in range(0x2320, 0x2321 + 1)]
    unicode_subset += [chr(code) for code in range(0x2329, 0x232a + 1)]
    # Box Drawing (00–7F)
    unicode_subset += [chr(code) for code in [0x2500,0x2502, 0x250c, 0x2510, 0x2514, 0x2518, 0x251c, 0x2524, 0x252c, 0x2534, 0x253c]]
    unicode_subset += [chr(code) for code in range(0x2550, 0x256c + 1)]
    # Block Elements (80–9F)
    unicode_subset += [chr(code) for code in [0x2580,0x2584, 0x2588, 0x258c]]
    unicode_subset += [chr(code) for code in range(0x2590, 0x2593 + 1)]
    # Geometric Shapes (A0–FF)
    # A0–A1, AA–AC, B2, BA, BC, C4, CA–CB, CF, D8–D9, E6
    unicode_subset += [chr(code) for code in range(0x25a0, 0x25a1 + 1)]
    unicode_subset += [chr(code) for code in range(0x25aa, 0x25ac + 1)]
    unicode_subset += [chr(code) for code in [0x25b2, 0x25ba, 0x25bc, 0x25c4, ]]
    unicode_subset += [chr(code) for code in range(0x25ca, 0x25cb + 1)]
    unicode_subset += [chr(code) for code in [0x25cf ]]
    unicode_subset += [chr(code) for code in range(0x25d8, 0x25d9 + 1)]
    unicode_subset += [chr(code) for code in [0x25e6 ]]
    # Miscellaneous Symbols (00–FF)
    unicode_subset += [chr(code) for code in range(0x263a, 0x263c + 1)]
    unicode_subset += [chr(code) for code in [0x2640,0x2642, 0x2660, 0x2663,   ]]
    unicode_subset += [chr(code) for code in range(0x2665, 0x2666 + 1)]
    unicode_subset += [chr(code) for code in [0x266a,0x266b     ]]
    # Private Use Area (00–FF ...)
    unicode_subset += [chr(code) for code in range(0x0f01, 0x0f02 + 1)]
    # Alphabetic Presentation Forms (00–4F)




    compare_chars(unicode_subset)


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
        self._start_x = 14
        self._start_y = 14

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
        contours1, _ = cv2.findContours(img_arr1, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        contours2, _ = cv2.findContours(img_arr2, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        simple_contour1 = self._simple_contour(contours1)
        simple_contour2 = self._simple_contour(contours2)
        # self._save_with_contours(ch1, img_arr1, simple_contour1)
        # self._save_with_contours(ch2, img_arr2, simple_contour2)
        scd = cv2.createShapeContextDistanceExtractor()
        dist = scd.computeDistance(simple_contour1, simple_contour2)
        return dist

    def _simple_contour(
        self, contours: t.Tuple, num_of_contours: int = 300
    ) -> np.ndarray:
        """
        Create simple contour.

        https://docs.opencv.org/4.8.0/d0/d38/modules_2shape_2samples_2shape_example_8cpp-example.html
        """
        tmp_contours = []
        for border in range(len(contours)):
            tmp_contours.extend(contours[border])

        # In case actual number of points is less than n, add element from the beginning
        for idx in itertools.cycle(range(len(tmp_contours))):
            if len(tmp_contours) >= num_of_contours:
                break
            tmp_contours.append(tmp_contours[idx])

        # Uniformly sampling
        random.shuffle(tmp_contours)
        out_contours = [tmp_contours[idx] for idx in range(num_of_contours)]
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
