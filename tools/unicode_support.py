#!/usr/bin/env python3

# Author: Mateusz Janda <mateusz janda at gmail com>
# Site: github.com/MateuszJanda/textmode-playground
# Ad maiorem Dei gloriam

import subprocess


def main():
    # https://en.wikipedia.org/wiki/Braille_Patterns
    check_unicode_support(0x28A7)
    check_unicode_support(ord("ぃ"))


def check_unicode_support(ch: int) -> None:
    """
    This function use fontconfig command line tools. Check if unicode character is support by
    available fonts.
    """

    charset = f"{ch:x}"
    # result = subprocess.run(["fc-list", f":charset={charset}:scalable=true:spacing=mono:", "file",
    result = subprocess.run(
        ["fc-list", f":charset={charset}", "file", "family", "fontformat"],
        stdout=subprocess.PIPE,
    )
    print(f"Character '{chr(ch)}' [0x{ch:x}] supported by:")
    for line in result.stdout.decode("utf-8").strip().split("\n"):
        print(line)


if __name__ == "__main__":
    main()
