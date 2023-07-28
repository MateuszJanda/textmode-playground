extern crate termion;

use std::fmt;
use termion::color::Color;
use termion::{color, style};
use tokio::time::Duration;
use rand::distributions::Alphanumeric;
use rand::{thread_rng, Rng};

// macro_rules! csi {
//     ($( $l:expr ),*) => { concat!("\x1B[", $( $l ),*) };

// }

#[derive(Copy, Clone, Debug)]
pub struct RichColor;

impl Color for RichColor {
    /// Example:
    /// echo -e "\033[38;2;255;0;0m\033[48;2;0;255;0mMy text"
    #[inline]
    fn write_fg(&self, f: &mut fmt::Formatter) -> fmt::Result {
        f.write_str(self.fg_str())
    }

    #[inline]
    fn write_bg(&self, f: &mut fmt::Formatter) -> fmt::Result {
        f.write_str(self.bg_str())
    }
}

impl RichColor {
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

struct DigitDrop {
    x: u16,
    y: u16,
    ch: char,
}

impl DigitDrop {
    /// one-based
    fn new(x: u16, y: u16) -> Self {
        assert!(x > 0 && y > 0);

        DigitDrop {
            x,
            y,
            ch: rand::thread_rng().sample(Alphanumeric) as char,
        }
    }

    fn print(&self) {
        print!("{}{}", termion::cursor::Goto(self.x, self.y), self.ch,);
    }

    fn go_down(&mut self) {
        self.y += 1;
    }

}

// TODO: http://www.rikai.com/library/kanjitables/kanji_codes.unicode.shtml

#[tokio::main]
async fn main() {
    // Get terminal size
    let (num_cols, num_rows) = termion::terminal_size().unwrap();
    // Hide cursor
    print!("{}", termion::cursor::Hide);
    // Clear screen
    print!("{}", termion::clear::All);

    // println!("Hello, world!");
    // println!("Size {:?}", termion::terminal_size());
    // // println!("Size {:?}", termion::terminal_size_pixels());
    // println!("{}Blue", color::Fg(color::Blue));
    // println!("{}{}RichColor", termion::cursor::Goto(5, 3), color::Fg(RichColor));



    // Init digit_drops
    let mut digit_drops = vec![];
    for x in 0..num_cols {
        if rand::thread_rng().gen_range(0..10) < 5 {
            digit_drops.push(DigitDrop::new(x + 1, 1));
        }
    }

    let mut interval = tokio::time::interval(Duration::from_millis(500));
    interval.tick().await;
    loop {
        for digit_drop in digit_drops.iter_mut() {
            if rand::thread_rng().gen_range(0..10) < 5 {
                digit_drop.go_down();
            }
            digit_drop.print();
        }

        interval.tick().await;
    }
}
