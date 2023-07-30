extern crate termion;

use std::fmt;

use std::io::{stdout, Stdout, Write};
use termion::screen::{AlternateScreen, IntoAlternateScreen};

use termion::color::Color;

use std::{thread, time};

use rand::distributions::Alphanumeric;
use rand::Rng;
use  std::collections::VecDeque;

#[derive(Copy, Clone, Debug)]
pub struct RichColor(pub usize);

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
        match self.0 {
            0 => "\x1B[38;2;255;255;0m",
            _ => "\x1B[38;2;255;0;0m",
        }
    }

    #[inline]
    /// Returns the ANSI escape sequences as a string.
    pub fn bg_str(&self) -> &'static str {
        // csi!("48;2;", $value, "m")
        "\x1B[48;2;0;255;255m"
    }
}

#[derive(Clone, Debug)]
struct DigitDrop {
    num_rows: usize,
    x: usize,
    y: usize,
    ch: char,
}

impl DigitDrop {
    /// one-based
    fn new(x: usize, y: usize, num_rows: usize) -> Self {
        DigitDrop {
            num_rows,
            x,
            y,
            ch: rand::thread_rng().sample(Alphanumeric) as char,
        }
    }

    fn print_drop(&self, screen: &mut AlternateScreen<Stdout>) {
        write!(
            screen,
            "{}{}{}",
            termion::cursor::Goto(self.x as u16 + 1, self.y as u16 + 1),
            termion::color::Fg(RichColor(0)),
            self.ch
        )
        .unwrap();
    }

    fn print_fade(&self, screen: &mut AlternateScreen<Stdout>, fade: usize) {
        if fade == FADE_LEN {
            write!(
                screen,
                "{} ",
                termion::cursor::Goto(self.x as u16 + 1, self.y as u16 + 1),
            )
            .unwrap();
        } else {
            write!(
                screen,
                "{}{}{}",
                termion::cursor::Goto(self.x as u16 + 1, self.y as u16 + 1),
                termion::color::Fg(RichColor(fade)),
                self.ch
            )
            .unwrap();
        }
    }

    fn fall_down(&mut self, buffer: &mut Vec<Vec<char>>) -> bool {
        self.y += 1;
        if self.y < buffer.len() {
            buffer[self.y][self.x] = self.ch;
            return true;
        }

        false
    }

    fn is_in_buffer(&self, buffer: &Vec<Vec<char>>) -> bool {
        buffer[self.y][self.x] == self.ch
    }

    fn is_out_of_screen(&self) -> bool {
        self.y > self.num_rows
    }
}

fn init_screen(screen: &mut AlternateScreen<Stdout>) {
    // Set background color to black
    write!(
        screen,
        "{}",
        termion::color::Bg(termion::color::Rgb(0, 0, 0))
    )
    .unwrap();
    // Hide cursor
    write!(screen, "{}", termion::cursor::Hide).unwrap();
    // Clear screen
    write!(screen, "{}", termion::clear::All).unwrap();
}

// TODO: http://www.rikai.com/library/kanjitables/kanji_codes.unicode.shtml

fn should_move_drop() -> bool {
    rand::thread_rng().gen_range(0..10) < 5
}

fn should_add_new_drop() -> bool {
    rand::thread_rng().gen_range(0..10) < 2
}

const FADE_LEN: usize = 5;

fn main() {
    let mut screen: AlternateScreen<Stdout> = stdout().into_alternate_screen().unwrap();
    init_screen(&mut screen);

    // Get terminal size
    let (num_cols, num_rows) = termion::terminal_size().unwrap();

    let mut buffer: Vec<Vec<char>> = vec![vec![' '; num_cols as usize]; num_cols as usize];
    let mut fades: VecDeque<Vec<DigitDrop>> = VecDeque::new();
    // Init digital drops
    let mut digit_drops = vec![];

    for x in 0..num_cols as usize {
        if rand::thread_rng().gen_range(0..10) < 7 {
            digit_drops.push(DigitDrop::new(x, 0, num_rows as usize));
        }
    }

    // digit_drops.push(DigitDrop::new(1, 0, num_rows as usize));
    // digit_drops.push(DigitDrop::new(3, 0, num_rows as usize));

    loop {
        // Fall drops
        let mut v: Vec<DigitDrop> = vec![];
        for digit_drop in digit_drops.iter_mut() {
            // if rand::thread_rng().gen_range(0..10) < 5 {
            if true {
                let is_fall = digit_drop.fall_down(&mut buffer);

                if is_fall {
                    v.push(digit_drop.clone());
                }
            }
        }

        // Remove all drops that are out of the screen
        digit_drops.retain(|digit_drop| !digit_drop.is_out_of_screen());

        // Draw digital drops
        for drop in digit_drops.iter() {
            drop.print_drop(&mut screen);
        }

        // Removed overalping fading
        for f in fades.iter_mut() {
            f.retain(|d| d.is_in_buffer(&buffer));
        }

        // Draw fading
        for (f, drops) in fades.iter().enumerate() {
            for drop in drops.iter() {
                drop.print_fade(&mut screen, f + 1);
            }
        }

        // Remove last fading
        if fades.len() == FADE_LEN {
            fades.pop_back();
        }


        // Copy digital drops to fades
        fades.push_front(v);

        // Add new drops
        if digit_drops.len() < 50 {
            for x in 0..num_cols {
                if should_add_new_drop() {
                    digit_drops.push(DigitDrop::new(x as usize, 0, num_rows as usize));
                }
            }
        }

        screen.flush().unwrap();
        thread::sleep(time::Duration::from_millis(100));
    }
}
