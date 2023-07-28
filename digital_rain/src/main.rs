extern crate termion;

use termion::{color, style};
use termion::color::Color;
use std::fmt;

macro_rules! csi {
    ($( $l:expr ),*) => { concat!("\x1B[", $( $l ),*) };

}


#[derive(Copy, Clone, Debug)]
pub struct Xxx;

impl Color for Xxx {
    // Example:
    // echo -e "\033[38;2;255;0;0m\033[48;2;0;255;0mXXX"
    #[inline]
    fn write_fg(&self, f: &mut fmt::Formatter) -> fmt::Result {
        f.write_str(self.fg_str())
    }

    #[inline]
    fn write_bg(&self, f: &mut fmt::Formatter) -> fmt::Result {
        f.write_str(self.bg_str())
    }
}

impl Xxx {
    #[inline]
    /// Returns the ANSI escape sequence as a string.
    pub fn fg_str(&self) -> &'static str {
        // csi!("38;2;", $value, "m")
        "\x1B[38;2;255;255;0m"
    }

    #[inline]
    /// Returns the ANSI escape sequences as a string.
    pub fn bg_str(&self) -> &'static str {
        // csi!("48;2;", $value, "m")
        "\x1B[48;2;0;255;255m"
    }
}

// TODO: http://www.rikai.com/library/kanjitables/kanji_codes.unicode.shtml

fn main() {
    println!("Hello, world!");
    println!("{}Blue", color::Fg(color::Blue));
    println!("{}XXX", color::Fg(Xxx));
}
