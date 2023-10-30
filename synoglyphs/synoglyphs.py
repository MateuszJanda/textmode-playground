#!/usr/bin/env python3

# Author: Mateusz Janda <mateusz janda at gmail com>
# Site: github.com/MateuszJanda/textmode-playground
# Ad maiorem Dei gloriam


import random
import time
import curses
import locale
import copy
import typing as t


THRESHOLD_CHANGE_CHAR = 0.5

CHAR_REPLACEMENTS = {
    "0": ["0", "ο", "о", "o", "θ", "O", "ɵ", "∁", "û", "ũ"],
    "1": ["1", "ɿ", "⁒", "ɪ", "⇣", "ℷ", "↓", "Ḭ", "₁", "˥"],
    "2": ["2", "ϩ", "ʡ", "ƶ", "z", "Ζ", "Ʃ", "Z", "ƻ", "ẑ"],
    "3": ["3", "ȝ", "ɜ", "З", "э", "ʒ", "Ȝ", "ӡ", "϶", "℈"],
    "4": ["4", "⋄", "₆", "⁶", "▵", "˨", "⁴", "∧", "⇖", "ₒ"],
    "5": ["5", "s", "S", "ƽ", "Ѕ", "פּ", "Б", "ѕ", "Ƽ", "6"],
    "6": ["6", "θ", "ѳ", "ƃ", "ɵ", "ϐ", "б", "Ƃ", "ε", "ẟ"],
    "7": ["7", "⁊", "?", "ʔ", "‽", "⅂", "Ὶ", "┑", "┐", "˥"],
    "8": ["8", "ϐ", "а", "ȣ", "B", "ѳ", "6", "θ", "В", "в"],
    "9": ["9", "פּ", "θ", "ɘ", "ɵ", "э", "ↄ", "ѳ", "϶", "פֿ"],
    "A": ["A", "А", "Α", "Ʌ", "Λ", "Á", "Å", "À", "∧", "Ά"],
    "B": ["B", "8", "В", "θ", "Β", "ϑ", "ȣ", "ʚ", "9", "3"],
    "C": ["C", "Ϲ", "с", "c", "ϲ", "Ⅽ", "ⅽ", "ℂ", "С", "∁"],
    "D": ["D", "Ο", "Ⅾ", "Ʋ", "ѻ", "ⅅ", "O", "Ͻ", "Ω", "ﬦ"],
    "E": ["E", "Е", "ℇ", "Ε", "s", "є", "Ȇ", "ϵ", "Ė", "6"],
    "F": ["F", "Ϝ", "Ғ", "P", "ғ", "Р", "г", "Ρ", "ₚ", "ₒ"],
    "G": ["G", "Ĝ", "Ǥ", "ϴ", "Ḡ", "ɢ", "Б", "⋳", "Ġ", "⊝"],
    "H": ["H", "н", "∺", "Η", "ʜ", "Н", "ℍ", "П", "↦", "м"],
    "I": ["I", "≀", "ⅈ", "₎", "₍", "l", "Ι", "⁾", "╹", "⁽"],
    "J": ["J", "∕", "/", "ⅉ", "ϳ", "ȷ", "ј", ")", "j", "Ј"],
    "K": ["K", "κ", "Ҝ", "Х", "ĸ", "ҝ", "к", "Κ", "Χ", "X"],
    "L": ["L", "Ⅼ", "╰", "┖", "¿", "┗", "└", "┕", "ʟ", "╙"],
    "M": ["M", "М", "м", "Ⅿ", "Μ", "и", "ʍ", "Ӎ", "ͷ", "н"],
    "N": ["N", "Ν", "ℕ", "ﬡ", "ℍ", "ы", "ⅳ", "Н", "ℝ", "ʁ"],
    "O": ["O", "Ο", "0", "ѻ", "О", "ɷ", "Ȏ", "○", "Ͻ", "⊖"],
    "P": ["P", "Ρ", "Р", "р", "p", "Þ", "ℙ", "ƿ", "ρ", "Ϸ"],
    "Q": ["Q", "Ο", "O", "О", "ℚ", "ѻ", "Ⅾ", "0", "⊘", "Ϥ"],
    "R": ["R", "ʀ", "Ɍ", "π", "∩", "Л", "п", "ℝ", "В", "Я"],
    "S": ["S", "ƽ", "Ѕ", "ѕ", "5", "Ƽ", "Ƃ", "З", "s", "6"],
    "T": ["T", "ϒ", "т", "┭", "┮", "┬", "Τ", "Ṭ", "⊤", "Т"],
    "U": ["U", "Ʋ", "Ư", "∐", "ѻ", "ц", "⊔", "Ų", "ṉ", "℧"],
    "V": ["V", "Ⅴ", "∨", "ѵ", "v", "Ṿ", "ṳ", "∇", "ṵ", "ⅴ"],
    "W": ["W", "Ẁ", "Ẉ", "ẇ", "w", "Ŵ", "Ẃ", "שּ", "ɴ", "Ⅶ"],
    "X": ["X", "Χ", "ⅹ", "Ⅹ", "х", "×", "Х", "x", "ҳ", "χ"],
    "Y": ["Y", "⋎", "Ү", "Υ", "γ", "ʏ", "ү", "∨", "Ɏ", "ϒ"],
    "Z": ["Z", "Ζ", "ℤ", "Ẑ", "2", "ƨ", "Ź", "z", "ƶ", "Ʃ"],
    "a": ["a", "а", "ө", "ѳ", "в", "э", "ɵ", "ʙ", "з", "ǝ"],
    "b": ["b", "ƅ", "ɒ", "ʋ", "ь", "ο", "þ", "Ϸ", "Ь", "Þ"],
    "c": ["c", "ϲ", "ⅽ", "с", "C", "ͼ", "Ϲ", "ɕ", "Ⅽ", "⁰"],
    "d": ["d", "ⅆ", "ⅾ", "ď", "σ", "ḋ", "α", "ő", "ɑ", "υ"],
    "e": ["e", "е", "ⅇ", "ε", "ƨ", "⊜", "о", "ʚ", "ͼ", "ℯ"],
    "f": ["f", "ŕ", "ǃ", "ṙ", "ř", "ȓ", "ṝ", "Ⅰ", "І", "↾"],
    "g": ["g", "ƍ", "ɡ", "º", "0", "σ", "ɑ", "ṵ", "ν", "∇"],
    "h": ["h", "ℎ", "һ", "Һ", "ŉ", "b", "ƅ", "ʰ", "ḩ", "הּ"],
    "i": ["i", "≀", "Ⅰ", "Ι", "ӏ", "ⅈ", "ⅰ", "/", "וֹ", "І"],
    "j": ["j", "∕", "/", "ϳ", "∫", "Ϳ", ")", "Ј", "ⅈ", "ј"],
    "k": ["k", "ĸ", "κ", "ҝ", "K", "ƙ", "K", "ₖ", "ḱ", "∎"],
    "l": ["l", "∕", "/", "ⅈ", "⁞", "≀", "\\", "╵", "Ӏ", "I"],
    "m": ["m", "₥", "ⅿ", "▗", "⇻", "∙", "∞", "ª", "▴", "ﬣ"],
    "n": ["n", "∩", "ƞ", "η", "л", "π", "п", "ɒ", "н", "ℴ"],
    "o": ["o", "о", "ο", "ɒ", "σ", "ɑ", "ө", "ѳ", "υ", "ơ"],
    "p": ["p", "ρ", "р", "ҏ", "ƿ", "ɒ", "P", "Þ", "Ϸ", "Ρ"],
    "q": ["q", "ɋ", "α", "ɑ", "ɥ", "ọ", "ς", "ҹ", "ǫ", "Ӵ"],
    "r": ["r", "╭", "ˤ", "ṛ", "┏", "┌", "┎", "┍", "г", "ʳ"],
    "s": ["s", "ѕ", "ŝ", "₅", "ɘ", "Ѕ", "ṣ", "϶", "S", "ş"],
    "t": ["t", "ἵ", "ṯ", "Ɩ", "ἰ", "τ", "ţ", "ₜ", "ɽ", "ἴ"],
    "u": ["u", "∪", "U", "⊎", "υ", "ư", "ʋ", "ṵ", "⊌", "⊍"],
    "v": ["v", "ⅴ", "∨", "ѵ", "⋎", "V", "ν", "ṿ", "▿", "⊌"],
    "w": ["w", "ͷ", "ʷ", "ₔ", "ư", "ₑ", "צּ", "ẉ", "↭", "ẇ"],
    "x": ["x", "ⅹ", "х", "×", "Χ", "Х", "Ⅹ", "X", "κ", "ҝ"],
    "y": ["y", "у", "У", "γ", "ⅴ", "ү", "ṿ", "⋎", "Ү", "ʸ"],
    "z": ["z", "ƶ", "₂", "ƨ", "²", "ẑ", "ɿ", "ʑ", "–", "ѫ"],
}


def main(scr: t.Any) -> None:
    """Update quote with homoglyphs and synoglyphs in loop."""
    setup_curses()
    scr.erase()

    quote = [
        list(),
        list(),
        list(
            "When you have eliminated the impossible, whatever remains, however improbable, must be the truth."
        ),
        list("   ~ Sherlock Holmes"),
    ]
    screen_buffer = copy.deepcopy(quote)

    while True:
        # replace_by_homoglyphs(quote, screen_buffer)
        replace_by_synoglyphs(quote, screen_buffer)

        refresh_screen(scr, screen_buffer)
        time.sleep(0.15)


def setup_curses() -> None:
    """Setup curses options."""
    curses.start_color()
    curses.use_default_colors()
    curses.halfdelay(1)
    curses.curs_set(False)


def replace_by_homoglyphs(quote: t.List[str], screen_buffer: t.List[str]) -> None:
    """
    Replace random chars by homoglyphs.
    - https://en.wikipedia.org/wiki/Homoglyph
    """
    for row_idx, line in enumerate(quote):
        for col_idx, ch in enumerate(line):
            if ch in CHAR_REPLACEMENTS and random.random() > THRESHOLD_CHANGE_CHAR:
                screen_buffer[row_idx][col_idx] = random.choice(CHAR_REPLACEMENTS[ch])
            else:
                screen_buffer[row_idx][col_idx] = ch


def replace_by_synoglyphs(quote: t.List[str], screen_buffer: t.List[str]) -> None:
    """
    Replace random chars by synoglyphs.

    `Synoglyphs are glyphs that look different but mean the same thing.`
    - https://en.wikipedia.org/wiki/Homoglyph
    """
    for row_idx, line in enumerate(quote):
        for col_idx, ch in enumerate(line):
            if ch in CHAR_REPLACEMENTS and random.random() > THRESHOLD_CHANGE_CHAR:
                screen_buffer[row_idx][col_idx] = random.choice(
                    CHAR_REPLACEMENTS[ch.upper()]
                )
            else:
                screen_buffer[row_idx][col_idx] = ch


def refresh_screen(scr: t.Any, screen_buffer: t.List) -> None:
    """Clear screen and print screen buffer content."""
    scr.erase()

    for num, line in enumerate(screen_buffer):
        scr.addstr(num, 0, "".join(line).encode("utf-8"))

    scr.refresh()


if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, "")
    curses.wrapper(main)
