#!/usr/bin/env python3

# Author: Mateusz Janda <mateusz janda at gmail com>
# Site: github.com/MateuszJanda/textmode-playground
# Ad maiorem Dei gloriam


import math
import collections as co
import sys
import time
import curses
import locale
import typing as t


BLANK_BRAILLE = 0x2800
BLANK_VALUE = 0x00
CELL_WIDTH = 2
CELL_HEIGHT = 4

Point = co.namedtuple("Point", ["x", "y"])


def main(scr: t.Any) -> None:
    """Rotate rectangles in loop."""
    setup_curses()
    scr.erase()

    rect1_center = Point(40, 50)
    rect1_points = [
        Point(40, 80),
        Point(70, 50),
        Point(40, 20),
        Point(10, 50),
    ]

    rect2_center = Point(110, 50)
    rect2_points = [
        Point(110, 80),
        Point(140, 50),
        Point(110, 20),
        Point(80, 50),
    ]

    angle = 0.1 / (2 * math.pi)

    while True:
        code_buffer = empty_code_buffer()
        screen_buffer = empty_screen_buffer()

        rect1_points = rotate_points(angle, rect1_center, rect1_points)
        rect2_points = rotate_points(angle, rect2_center, rect2_points)

        draw_figure(rect1_points, code_buffer, screen_buffer, code_to_braille)
        # draw_figure(rect2_points, code_buffer, screen_buffer, code_to_ascii)
        draw_figure(rect2_points, code_buffer, screen_buffer, code_to_unicode_subset)

        refresh_screen(scr, screen_buffer)
        time.sleep(0.02)

    curses.endwin()


def setup_curses() -> None:
    """Setup curses options."""
    curses.start_color()
    curses.use_default_colors()
    curses.halfdelay(1)
    curses.curs_set(False)


def rotate_points(angle: float, center_pt: Point, points: t.List) -> t.List:
    """Rotate points by given angle."""
    result = []
    for pt in points:
        vec = Point(pt.x - center_pt.x, pt.y - center_pt.y)
        nx = vec.x * math.cos(angle) - vec.y * math.sin(angle)
        ny = vec.x * math.sin(angle) + vec.y * math.cos(angle)

        result.append(Point(center_pt.x + nx, center_pt.y + ny))

    return result


def draw_figure(
    points: t.List, code_buffer: t.List, screen_buffer: t.List, draw_code: t.Callable
) -> None:
    """Draw lines between points."""
    for start, end in zip(points, points[1:] + [points[0]]):
        start = Point(int(start.x), int(start.y))
        end = Point(int(end.x), int(end.y))
        draw_line(start, end, code_buffer, screen_buffer, draw_code)


def draw_line(
    pt1: Point,
    pt2: Point,
    code_buffer: t.List,
    screen_buffer: t.List,
    draw_code: t.Callable,
) -> None:
    """
    Draw line - Bresenham's line algorithm
    - https://pl.wikipedia.org/wiki/Algorytm_Bresenhama
    """
    x, y = pt1.x, pt1.y

    # Drawing direction
    if pt1.x < pt2.x:
        xi = 1
        dx = pt2.x - pt1.x
    else:
        xi = -1
        dx = pt1.x - pt2.x

    if pt1.y < pt2.y:
        yi = 1
        dy = pt2.y - pt1.y
    else:
        yi = -1
        dy = pt1.y - pt2.y

    set_point(Point(x, y), code_buffer)
    draw_code(Point(x, y), code_buffer, screen_buffer)

    # X axis
    if dx > dy:
        ai = (dy - dx) * 2
        bi = dy * 2
        d = bi - dx
        while x != pt2.x:
            # Coordinate test
            if d >= 0:
                x += xi
                y += yi
                d += ai
            else:
                d += bi
                x += xi
            set_point(Point(x, y), code_buffer)
            draw_code(Point(x, y), code_buffer, screen_buffer)
    # Y axis
    else:
        ai = (dx - dy) * 2
        bi = dx * 2
        d = bi - dy
        while y != pt2.y:
            # Coordinate test
            if d >= 0:
                x += xi
                y += yi
                d += ai
            else:
                d += bi
                y += yi
            set_point(Point(x, y), code_buffer)
            draw_code(Point(x, y), code_buffer, screen_buffer)


def set_point(pt: Point, code_buffer: t.List) -> None:
    """Set code as bit (unicode braille dot numbering) in cell."""
    row = curses.LINES - 1 - int(pt.y / CELL_HEIGHT)
    if row < 0:
        return

    col = int(pt.x / CELL_WIDTH)
    code_buffer[row][col] |= point_to_code(pt.y, pt.x)


def point_to_code(y: int, x: int) -> int:
    """Calculate braille dot number from point position."""
    bx = x % CELL_WIDTH
    by = y % CELL_HEIGHT

    if bx == 0:
        if by == 0:
            return 0x40
        else:
            return 0x4 >> (by - 1)
    else:
        if by == 0:
            return 0x80
        else:
            return 0x20 >> (by - 1)


def code_to_braille(pt: Point, code_buffer: t.List, screen_buffer: t.List) -> None:
    """Translate cell code (braille dot number) to proper Braille code."""
    row = curses.LINES - 1 - int(pt.y / CELL_HEIGHT)
    if row < 0:
        return

    col = int(pt.x / CELL_WIDTH)
    screen_buffer[row][col] = chr(BLANK_BRAILLE | code_buffer[row][col])


def code_to_ascii(pt: Point, code_buffer: t.List, screen_buffer: t.List) -> None:
    """
    Translate cell code (braille dot number) to ASCII character.

    Extracted from:
    https://github.com/MateuszJanda/textmode-playground/tools/braille_to_ascii.csv
    """
    code_replacement = (
        "!....;..._.r:rrr..-L.\".+.-'=.F,\"....-,>L;-c=--sP..-,'`=`.,,',,,a"
        ".::'..l..-.f...l:7?\".iI\".-'P..ir.,.l_r\"l..cFs_Fr,.F_s,\"F.',',F.S"
        "......L.:-`-,,.P:,'_,tct.?,E,S-a....,,,,.,,7-lc_;,7'',,_.,.,.;'*"
        "_--.LL.L,-8.__:\\-ZFF=sFl``,e6__s',,\\=P\"L','.E5*5',,t,cct'7.F'',E"
    )

    row = curses.LINES - 1 - int(pt.y / CELL_HEIGHT)
    if row < 0:
        return

    col = int(pt.x / CELL_WIDTH)
    screen_buffer[row][col] = code_replacement[code_buffer[row][col]]


def code_to_unicode_subset(
    pt: Point, code_buffer: t.List, screen_buffer: t.List
) -> None:
    """
    Translate cell code (braille dot number) to Unicode character.

    Extracted from:
    https://github.com/MateuszJanda/textmode-playground/tools/braille_to_unicode_subset.csv
    """
    code_replacement = (
        " ‧‧‧‧:‧⁝‧‥˙ͱ:┎‧г‧˙‥↳·ͱ↱ʺ.⁖͵=˓ℴⅎ∍‧ˑ˙╰‥∴ʱ└:˦⁖דּ˨‥ⅎ϶:·⁖⁘⁖ₕʰͱ⁝͵‵דּ’ʻⅎ⁼"
        "‧;;⁝.‧⁝·⁚′′┌․˗᾽˙∶Ͱ∵Ͱ˙Γ┌⋅⁝´ˈ⊧᾽P᾽⊦‧′ͱ╵↱ˑʺ∙⋅ƨʽF˙ͱ·פּ˩`ℐͱ⁘ͱ┈ʱ‘ʻ·,,ͺ◜ͱ"
        "‧˓⁚ʿ.ʹרּ͵;᾿·₋⁖ʗⅎɽ;,∵ךּ⁖Ŀϛ‵⁝´⁖ךּ˨Ĳˊⅽ․‧․⋅⁖ͺ⁘˙⁝‘,˧,;דּɴ⁝ʹ͵‚⁖,‘ₒ·᾽˙ʹʹʼ‚⁷"
        "‥╴‐Ĺь└ʟ⁽᾿⁚′·–╺∍קּ∴‑⁚‼Ⅎв϶‼᾽ˑ῀‼┚‒‼‼’ʻₕ⊦=ьͱı‘ʹℐ.Ⅎ‒ɔℐʹʻ‚ʾ⁖΄ₒʰ͵,.ʼ⁖ʼₚₒ"
    )

    row = curses.LINES - 1 - int(pt.y / CELL_HEIGHT)
    if row < 0:
        return

    col = int(pt.x / CELL_WIDTH)
    screen_buffer[row][col] = code_replacement[code_buffer[row][col]]


def empty_code_buffer() -> t.List:
    """Create empty code buffer."""
    code_buffer = []
    for _ in range(curses.LINES):
        code_buffer.append([BLANK_VALUE] * (curses.COLS - 1))

    return code_buffer


def empty_screen_buffer() -> t.List:
    """Create empty screen buffer."""
    screen_buffer = []
    for _ in range(curses.LINES):
        screen_buffer.append([" "] * (curses.COLS - 1))

    return screen_buffer


def refresh_screen(scr: t.Any, screen_buffer: t.List) -> None:
    """Clear screen and print screen buffer content."""
    # https://stackoverflow.com/questions/24964940/python-curses-tty-screen-blink
    scr.erase()

    for num, line in enumerate(screen_buffer):
        scr.addstr(num, 0, "".join(line).encode("utf-8"))

    scr.refresh()


def setup_stderr() -> None:
    """Redirect stderr to other terminal. Run tty command, to get terminal id."""
    sys.stderr = open("/dev/pts/2", "w")


def eprint(*args: t.Tuple, **kwargs: t.Dict) -> None:
    """Print on stderr."""
    print(*args, file=sys.stderr)


if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, "")
    # setup_stderr()
    curses.wrapper(main)
