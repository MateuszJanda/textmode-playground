#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
import locale
import time

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
    scr.refresh()

    while not check_exit_key(scr):
        time.sleep(0.1)


def check_exit_key(scr):
    ch = scr.getch()
    return ch == ord('q')


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(main)
