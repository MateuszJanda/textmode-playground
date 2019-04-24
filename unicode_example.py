#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import curses
import locale
import time
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

    while not check_exit_key(scr):
        time.sleep(0.1)


def char_support(scr, character=unichr(0x28a7)):
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


def check_exit_key(scr):
    ch = scr.getch()
    return ch == ord('q')


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(main)
