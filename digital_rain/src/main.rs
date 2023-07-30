extern crate termion;

use std::fmt;

use std::io::{stdout, Stdout, Write};
use termion::screen::{AlternateScreen, IntoAlternateScreen};

use termion::color::Color;

use std::{thread, time};

use rand::distributions::Alphanumeric;
use rand::Rng;

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

#[derive(Clone, Debug)]
struct Cell {
    ch: char,
    dt: u32,
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

    // fn print(&self) {
    //     print!("{}{}", termion::cursor::Goto(self.x, self.y), self.ch);
    // }

    // fn text(&self) -> String {
    //     format!(
    //         "{}{}",
    //         termion::cursor::Goto(self.x as u16 + 1, self.y as u16 + 1),
    //         self.ch
    //     )
    // }

    fn print(&self, screen: &mut AlternateScreen<Stdout>) {
        write!(
            screen,
            "{}{}{}",
            termion::cursor::Goto(self.x as u16 + 1, self.y as u16 + 1),
            termion::color::Fg(RichColor),
            self.ch
        )
        .unwrap();
    }

    fn fall_down(&mut self, buffer: &mut Vec<Vec<char>>) {
        self.y += 1;
        if self.y < buffer.len() {
            buffer[self.y ][self.x] = self.ch;
        }
    }

    // fn go_down(&mut self) {
    //     self.old_y = self.y;
    //     self.y += 1;
    // }

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
    // let mut buffer = vec![vec![Cell { ch: ' ', dt: 0 }; num_cols as usize]; num_cols as usize];
    let mut buffer: Vec<Vec<char>> = vec![vec![' '; num_cols as usize]; num_cols as usize];
    let mut fades: Vec<Vec<DigitDrop>> = vec![];

    // println!("Hello, world!");
    // println!("Size {:?}", termion::terminal_size());
    // // println!("Size {:?}", termion::terminal_size_pixels());
    // println!("{}Blue", color::Fg(color::Blue));
    // println!("{}{}RichColor", termion::cursor::Goto(5, 3), color::Fg(RichColor));

    // Init digital drops
    let mut digit_drops = vec![];
    for x in 0..num_cols as usize {
        if rand::thread_rng().gen_range(0..10) < 5 {
            digit_drops.push(DigitDrop::new(x, 0, num_rows as usize));
        }
    }

    loop {
        // Fall drops
        for digit_drop in digit_drops.iter_mut() {
            if rand::thread_rng().gen_range(0..10) < 5 {
                digit_drop.fall_down(&mut buffer);
            }
        }

        // Draw digital drops
        for drop in digit_drops.iter() {
            drop.print(&mut screen);
        }

        // Removed overalping fading
        for f in fades.iter_mut() {
            f.retain(|d| d.is_in_buffer(&buffer) );
        }

        // Draw fading
        for drops in fades.iter() {
            for drop in drops.iter() {
                drop.print(&mut screen);
            }
        }
        // Remove last fading
        if fades.len() == FADE_LEN {
            fades.pop();
        }

        // Remove all drops that are out of the screen
        digit_drops.retain(|digit_drop| !digit_drop.is_out_of_screen());


        // Copy digital drops to fades
        let mut v: Vec<DigitDrop> = vec![];
        for d in digit_drops.iter() {
            v.push(d.clone());
        }
        fades.push(v);

        // Add new drops
        if digit_drops.len() < 50 {
            for x in 0..num_cols {
                if should_add_new_drop() {
                    digit_drops.push(DigitDrop::new(x as usize, 0, num_rows as usize));
                }
            }
        }

        screen.flush().unwrap();
        thread::sleep(time::Duration::from_millis(5));
    }
}
