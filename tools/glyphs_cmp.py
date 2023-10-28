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


FONT_SIZE = 200
IMG_WIDTH = 300
IMG_HEIGHT = 300


def main() -> None:
    # gly_cmp = GlyphCmp()
    # gly = GlyphDrawer(
    #     font_name="DejaVuSansMono",
    #     font_path="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    # )

    # gly = GlyphDrawer(
    #     font_name="DejaVuSans",
    #     font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    # )

    # print_distance = lambda ch1, ch2: print(
    #     f"Distance {ch1} <-> {ch2} : {gly_cmp.distance(ch1, gly, ch2, gly)}"
    # )

    # print_distance("i", "⢷")

    # TODO: Maybe '_' should be used to calculate area?
    # assert is_wide_char('█', "DejaVuSans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf") == False

    # ==========================================================================


    calc_distances_all(ascii_all(), "ascii_all.csv")
    # calc_distances(unicode_braille(), ascii_all(), "braille_to_ascii.csv")
    # calc_distances(
    #     unicode_braille(),
    #     unicode_standardized_subset(),
    #     "braille_to_unicode_subset.csv",
    # )


def unicode_standardized_subset() -> t.List:
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

    return unicode_subset


def unicode_braille() -> t.List:
    """
    https://en.wikipedia.org/wiki/Braille_Patterns
    """

    return [chr(code) for code in range(0x2800, 0x28FF)]


def ascii_all() -> t.List:
    """
    https://en.wikipedia.org/wiki/ASCII
    """
    return list(string.digits + string.ascii_letters + string.punctuation)


def is_wide_char(ch: str, font_name: str, font_path: str) -> bool:
    """
    Check if character for given font is wider than standard one.
    """
    # Standard area of monospace font
    standard_gly = GlyphDrawer(
        font_name="DejaVuSansMono",
        font_path="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    )
    x1, _, x2, _ = standard_gly.get_area()
    mono_width = x2 - x1 + 1

    gly = GlyphDrawer(font_name, font_path)
    return gly.is_wide(ch, mono_width)


def calc_distances(key_set1: str, value_set: str, file_name: str) -> None:
    """
    Calculate distances between all characters.
    """
    # gly = GlyphDrawer(
    #     font_name="DejaVuSansMono",
    #     font_path="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    # )
    gly = GlyphDrawer(
        font_name="DejaVuSans",
        font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    )
    print(f"Font area (x1, y1, x2, y2): {gly.get_area()}")

    gly_cmp = GlyphCmp()
    count_fail = 0
    count_not_supported = 0

    distances = defaultdict(dict)
    all_pairs = list(itertools.product(key_set1, value_set))
    for key_ch, val_ch in tqdm(all_pairs):
        if key_ch == val_ch:
            distances[key_ch][val_ch] = 0
        elif key_ch in distances and val_ch in distances[key_ch]:
            # Distances already calculated, so skip
            continue
        elif not gly.is_supported(key_ch) or not gly.is_supported(val_ch):
            # If one of the chars is not supported then can't calculate distance
            print(f"Not supported : {key_ch} <-> {val_ch}")
            distances[key_ch][val_ch] = -1
            count_not_supported += 1
        else:
            try:
                dist = gly_cmp.distance(key_ch, gly, val_ch, gly)
                distances[key_ch][val_ch] = dist
                # print(f"Distance : {key_ch} <-> {val_ch} : {dist}")
            except:
                print(f"Fail : {key_ch} <-> {val_ch}")
                distances[key_ch][val_ch] = -1
                count_fail += 1

    export_distances_to_csv(distances, file_name)

    print(f"All cases: {len(all_pairs)}")
    print(f"Failed: {count_fail}, ")
    print(f"Not supported: {count_not_supported}")
    print(
        f"Success rate: {((len(all_pairs) - (count_fail + count_not_supported)) / len(all_pairs)) * 100:.2f}%"
    )


def calc_distances_all(ch_set: str, file_name: str) -> None:
    """
    Calculate distances between all characters.
    """
    gly = GlyphDrawer(
        font_name="DejaVuSansMono",
        font_path="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    )
    print(f"Font area (x1, y1, x2, y2): {gly.get_area()}")

    gly_cmp = GlyphCmp()
    count_fail = 0
    count_not_supported = 0

    distances = defaultdict(dict)
    all_pairs = list(itertools.combinations(ch_set, 2))
    for ch1, ch2 in tqdm(all_pairs):
        if (ch1 in distances and ch2 in distances[ch1]) or (
            ch2 in distances and ch1 in distances[ch2]
        ):
            # Distances already calculated, so skip
            continue
        elif not gly.is_supported(ch1) or not gly.is_supported(ch2):
            # If one of the chars is not supported then can't calculate distance
            print(f"Not supported : {ch1} <-> {ch2}")
            distances[ch1][ch2] = -1
            distances[ch2][ch1] = -1
            count_not_supported += 1
        else:
            try:
                dist = gly_cmp.distance(ch1, gly, ch2, gly)
                distances[ch1][ch2] = dist
                distances[ch2][ch1] = dist
                # print(f"Distance : {ch1} <-> {ch2} : {dist}")
            except:
                print(f"Fail : {ch1} <-> {ch2}")
                distances[ch1][ch2] = -1
                distances[ch2][ch1] = -1
                count_fail += 1

    for ch in ch_set:
        distances[ch][ch] = 0

    export_distances_to_csv(distances, file_name)

    print(f"All cases: {len(all_pairs)}")
    print(f"Failed: {count_fail}, ")
    print(f"Not supported: {count_not_supported}")
    print(
        f"Success rate: {((len(all_pairs) - (count_fail + count_not_supported)) / len(all_pairs)) * 100:.2f}%"
    )


def export_distances_to_csv(distances: t.Dict, file_name: str) -> None:
    """
    Export shape distances to .csv.
    """
    with open(f"{file_name}", "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        # Write row with values codes
        first_key = list(distances.keys())[0]
        writer.writerow(
            [f"0x{0:04x}"]
            + [f"0x{ord(col_ch):04x}" for col_ch in sorted(distances[first_key].keys())]
        )
        # Write rows with distances for for each key (code)
        keys = sorted(distances.keys())
        for key_ch in keys:
            row = [f"0x{ord(key_ch):04x}"] + [
                f"{distances[key_ch][val_ch]:.4f}"
                for val_ch in sorted(distances[key_ch].keys())
            ]
            writer.writerow(row)


class GlyphDrawer:
    """
    Glyph drawer by specified font.
    """

    def __init__(
        self,
        font_name: str,
        font_path: str,
        font_size: int = FONT_SIZE,
        img_width: int = IMG_WIDTH,
        img_height: int = IMG_HEIGHT,
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
        dil_arr1 = cv2.dilate(
            img_arr1, cv2.getStructuringElement(cv2.MORPH_RECT, (23, 23))
        )
        dil_arr2 = cv2.dilate(
            img_arr2, cv2.getStructuringElement(cv2.MORPH_RECT, (23, 23))
        )

        contours1, _ = cv2.findContours(dil_arr1, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        contours2, _ = cv2.findContours(dil_arr2, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        if len(contours1) == 0 or len(contours2) == 0:
            return -1

        contour1 = self._simple_contour(contours1)
        contour2 = self._simple_contour(contours2)

        # self._save_with_contours(ch1, img_arr1, contour1)
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
        for border in contours:
            tmp_contour.extend(border)

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
