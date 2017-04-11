#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import urwid

# txt = urwid.Text(u"Hello World")
# fill = urwid.Filler(txt, 'top')
# loop = urwid.MainLoop(fill)
# loop.run()

"""
http://stackoverflow.com/questions/1279341/how-do-i-use-extended-characters-in-pythons-curses-library
https://en.wikipedia.org/wiki/Braille_Patterns
"""

import curses
import locale

locale.setlocale(locale.LC_ALL, '')    # set your locale

scr = curses.initscr()
scr.clear()
scr.addstr(0, 0, u'\u3042'.encode('utf-8'))
scr.addstr(1, 0, u'\u2875'.encode('utf-8'))
# scr.addstr('asdf')
scr.refresh()


while True:
    # This blocks (waits) until the time has elapsed, or there is input to be handled
    char = scr.getch()
    scr.clear()

    if char == ord('q'):
        break

# here implement simple code to wait for user input to quit
curses.endwin()
