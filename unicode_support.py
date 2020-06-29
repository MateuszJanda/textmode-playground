#!/usr/bin/env python3

"""
Author: Mateusz Janda <mateusz janda at gmail com>
Site: github.com/MateuszJanda/textmode-playground
Ad maiorem Dei gloriam
"""

import curses
import locale
import fontconfig

"""
Useful links:
http://stackoverflow.com/questions/1279341/how-do-i-use-extended-characters-in-pythons-curses-library
https://en.wikipedia.org/wiki/Braille_Patterns
"""

def main(scr):
    scr.clear()
    scr.addstr(0, 0, u'\u3042'.encode('utf-8'))
    scr.addstr(1, 0, u'\u2875'.encode('utf-8'))
    scr.addstr(2, 0, 'asdf')

    char_support(scr)

    scr.refresh()
    scr.getch()


def char_support(scr, character=chr(0x28a7)):
    font_names = fontconfig.query()
    row = 4

    for name in font_names:
        font = fontconfig.FcFont(name)
        if font.has_char(character) and font.fullname:
            # info = font.file
            # info = font.fullname[0][1] + ' [' + str(font.spacing) + ']'
            info = str(font.fullname)
            scr.addstr(row, 0, info)
            row += 1


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(main)
