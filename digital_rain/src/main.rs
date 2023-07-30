extern crate termion;

use rand::distributions::Alphanumeric;
use rand::Rng;
use std::collections::VecDeque;
use std::fmt;
use std::io::{stdout, Stdout, Write};
use std::{thread, time};
use termion::color::Color;
use termion::screen::{AlternateScreen, IntoAlternateScreen};

const NUM_OF_DROPS: usize = 5;
const NUM_OF_NEW_DROPS: usize = 1;
const NUM_OF_FADING_LEVELS: usize = 5;
const INIT_DROPS_PROB: u32 = 70;

/// This type make use of extended ANSI to display "true colors" (24-bit/RGB values)
/// - https://en.wikipedia.org/wiki/ANSI_escape_code#SGR_(Select_Graphic_Rendition)_parameters
/// - https://en.wikipedia.org/wiki/ANSI_escape_code#24-bit
///
/// It translate "fading level" value to one of predefined RGB values.
///
/// Test in terminal Example:
/// echo -e "\033[38;2;255;0;0m\033[48;2;0;255;0mMy text"
#[derive(Copy, Clone, Debug)]
pub struct FadeColor(pub usize);

impl Color for FadeColor {
    #[inline]
    fn write_fg(&self, f: &mut fmt::Formatter) -> fmt::Result {
        f.write_str(self.fg_str())
    }

    #[inline]
    fn write_bg(&self, f: &mut fmt::Formatter) -> fmt::Result {
        f.write_str(self.bg_str())
    }
}

impl FadeColor {
    #[inline]
    /// Returns the ANSI escape sequence as a string (&'static str).
    pub fn fg_str(&self) -> &'static str {
        // csi!("38;2;", $value, "m")
        match self.0 {
            0 => "\x1B[38;2;255;255;0m",
            _ => "\x1B[38;2;255;0;0m",
        }
    }

    #[inline]
    /// Returns the ANSI escape sequences as a string (&'static str).
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
    speed_step: u32,
}

impl DigitDrop {
    fn new(x: usize, y: usize, num_rows: usize) -> Self {
        DigitDrop {
            num_rows,
            x,
            y,
            ch: rand::thread_rng().sample(Alphanumeric) as char,
            speed_step: rand::thread_rng().gen_range(1..10),
        }
    }

    /// Print digital drop.
    fn print_drop(&self, screen: &mut AlternateScreen<Stdout>) {
        // ANSI position (used by Goto) start from one.
        write!(
            screen,
            "{}{}{}",
            termion::cursor::Goto(self.x as u16 + 1, self.y as u16 + 1),
            termion::color::Fg(FadeColor(0)),
            self.ch
        )
        .unwrap();
    }

    /// Print fading after drop goes down.
    fn print_fade(&self, screen: &mut AlternateScreen<Stdout>, fade_level: usize) {
        // ANSI position (used by Goto) start from one.
        match fade_level {
            // If this is last fading phase then clear character on screen.
            NUM_OF_FADING_LEVELS => write!(
                screen,
                "{} ",
                termion::cursor::Goto(self.x as u16 + 1, self.y as u16 + 1),
            )
            .unwrap(),
            _ => write!(
                screen,
                "{}{}{}",
                termion::cursor::Goto(self.x as u16 + 1, self.y as u16 + 1),
                termion::color::Fg(FadeColor(fade_level)),
                self.ch
            )
            .unwrap(),
        }
    }

    /// Move drop down but only if current "step" match "speed_step".
    /// Method return if drop was moved or not.
    fn go_down(&mut self, buffer: &mut Vec<Vec<char>>, step: u32) -> bool {
        // Check if drop should fall in this step.
        if step % self.speed_step != 0 {
            return false;
        }

        self.y += 1;
        if self.y < buffer.len() {
            buffer[self.y][self.x] = self.ch;
            return true;
        }

        false
    }

    /// Check if character in buffer and "digit drop" character at same position are same.
    fn is_in_buffer(&self, buffer: &Vec<Vec<char>>) -> bool {
        buffer[self.y][self.x] == self.ch
    }

    /// Check if drop if out of the screen.
    fn is_out_of_screen(&self) -> bool {
        self.y > self.num_rows
    }
}

fn init_screen(screen: &mut AlternateScreen<Stdout>) {
    // Set background color to black.
    write!(
        screen,
        "{}",
        termion::color::Bg(termion::color::Rgb(0, 0, 0))
    )
    .unwrap();
    // Hide cursor.
    write!(screen, "{}", termion::cursor::Hide).unwrap();
    // Clear screen.
    write!(screen, "{}", termion::clear::All).unwrap();
}

// TODO: http://www.rikai.com/library/kanjitables/kanji_codes.unicode.shtml
fn main() {
    // Init screen.
    let mut screen: AlternateScreen<Stdout> = stdout().into_alternate_screen().unwrap();
    init_screen(&mut screen);

    // Get terminal size
    let (num_cols, num_rows) = termion::terminal_size().unwrap();

    // Init data
    let mut buffer: Vec<Vec<char>> = vec![vec![' '; num_cols as usize]; num_cols as usize];
    let mut fades: VecDeque<Vec<DigitDrop>> = VecDeque::new();
    let mut digit_drops = vec![];

    // for x in 0..num_cols as usize {
    //     if rand::thread_rng().gen_range(0..100) < INIT_DROPS_PROB {
    //         digit_drops.push(DigitDrop::new(x, 0, num_rows as usize));
    //     }
    // }

    digit_drops.push(DigitDrop::new(1, 0, num_rows as usize));
    digit_drops.push(DigitDrop::new(3, 0, num_rows as usize));

    let mut step = 0;
    loop {
        // Trigger all drops to check if the should be moved or not.
        let mut fading_drops: Vec<DigitDrop> = vec![];
        for digit_drop in digit_drops.iter_mut() {
            let is_moved = digit_drop.go_down(&mut buffer, step);
            if is_moved {
                fading_drops.push(digit_drop.clone());
            }
        }

        // Remove all drops that are out of the screen.
        digit_drops.retain(|digit_drop| !digit_drop.is_out_of_screen());

        // Draw digital drops.
        for digit_drop in digit_drops.iter() {
            digit_drop.print_drop(&mut screen);
        }

        // Removed overlapping drop fading with real digital drop.
        for f in fades.iter_mut() {
            f.retain(|d| d.is_in_buffer(&buffer));
        }

        // Draw fading drops.
        for (fade_level, drops) in fades.iter().enumerate() {
            for drop in drops.iter() {
                drop.print_fade(&mut screen, fade_level + 1);
            }
        }

        // Remove last fading
        if fades.len() == NUM_OF_FADING_LEVELS {
            fades.pop_back();
        }

        // Digital drops will fade from this point.
        fades.push_front(fading_drops);

        // Add new drops.
        // let mut i = 0;
        // while i < NUM_OF_NEW_DROPS && digit_drops.len() < NUM_OF_DROPS {
        //     digit_drops.push(DigitDrop::new(
        //         rand::thread_rng().gen_range(0..num_cols) as usize,
        //         0,
        //         num_rows as usize,
        //     ));
        //     i += 1;
        // }

        screen.flush().unwrap();
        thread::sleep(time::Duration::from_millis(100));
        step += 1;
    }
}
