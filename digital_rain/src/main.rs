extern crate termion;

use rand::distributions::Alphanumeric;
use rand::Rng;
use std::collections::VecDeque;
use std::fmt;
use std::io::{stdout, Stdout, Write};
use std::{thread, time};
use termion::color::Color;
use termion::screen::{AlternateScreen, IntoAlternateScreen};

const NUM_OF_INIT_DROPS: usize = 40;
const NUM_OF_NEW_DROPS: usize = 10;
const NUM_OF_FADING_LEVELS: usize = 16;
const DROPS_IN_SCREEN: f32 = 0.7;

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
    /// Returns the ANSI escape sequence for foreground color (RGB) as a string (&'static str).
    pub fn fg_str(&self) -> &'static str {
        // csi!("38;2;", $value, "m")
        match self.0 {
            0 => "\x1B[38;2;0;255;0m",
            1 => "\x1B[38;2;0;240;0m",
            2 => "\x1B[38;2;0;224;0m",
            3 => "\x1B[38;2;0;208;0m",
            4 => "\x1B[38;2;0;192;0m",
            5 => "\x1B[38;2;0;176;0m",
            6 => "\x1B[38;2;0;160;0m",
            7 => "\x1B[38;2;0;144;0m",
            8 => "\x1B[38;2;0;128;0m",
            9 => "\x1B[38;2;0;112;0m",
            10 => "\x1B[38;2;0;96;0m",
            11 => "\x1B[38;2;0;80;0m",
            12 => "\x1B[38;2;0;64;0m",
            13 => "\x1B[38;2;0;48;0m",
            14 => "\x1B[38;2;0;32;0m",
            15 => "\x1B[38;2;0;16;0m",
            _ => "\x1B[38;2;255;0;0m",
        }
    }

    #[inline]
    /// Returns the ANSI escape sequences for background RGB color (black) as a string (&'static str).
    pub fn bg_str(&self) -> &'static str {
        // csi!("48;2;", $value, "m")
        "\x1B[48;2;0;0;0m"
    }
}

#[derive(Clone, Debug)]
struct DigitDrop {
    x: usize,
    y: usize,
    num_rows: usize,
    ch: char,
    speed_step: u32,
}

impl DigitDrop {
    fn new(x: usize, y: usize, num_rows: usize) -> Self {
        let ch = rand::thread_rng().sample(Alphanumeric) as char;
        DigitDrop {
            x,
            y,
            num_rows,
            ch,
            speed_step: rand::thread_rng().gen_range(1..6),
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
    /// Method return previous drop/position if something changed.
    fn go_down(&mut self, step: u32) {
        // Check if drop should fall in this step.
        if step % self.speed_step != 0 {
            return;
        }

        self.y += 1;
    }

    /// Check if drop if out of the screen.
    fn is_out_of_screen(&self) -> bool {
        self.y > self.num_rows
    }
}

/// Init screen (set background, hide cursor and clear screen).
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
    let num_of_drops: usize = ((num_cols * num_rows) as f32 * DROPS_IN_SCREEN) as usize;

    // Init data
    let mut fades: VecDeque<Vec<DigitDrop>> = VecDeque::new();
    let mut digit_drops: Vec<DigitDrop> = vec![];

    for _ in 0..NUM_OF_INIT_DROPS {
        digit_drops.push(DigitDrop::new(
            rand::thread_rng().gen_range(0..num_cols) as usize,
            0,
            num_rows as usize,
        ));
    }

    // digit_drops.push(DigitDrop::new(1, 0, num_rows as usize));

    let mut step = 1;
    loop {
        // Trigger all drops to check if the should be moved or not.
        let mut fading_drops: Vec<DigitDrop> = vec![];
        for digit_drop in digit_drops.iter_mut() {
            fading_drops.push(digit_drop.clone());
            digit_drop.go_down(step);
            digit_drop.print_drop(&mut screen);
        }

        // Update. Digital drops will fade from this point.
        fades.push_front(fading_drops);

        // Draw fading drops.
        for (fade_level, drops) in fades.iter().enumerate() {
            for fade_drop in drops.iter() {
                fade_drop.print_fade(&mut screen, fade_level + 1);
            }
        }

        // Remove all drops that are out of the screen.
        digit_drops.retain(|digit_drop| !digit_drop.is_out_of_screen());

        // Remove last fading
        if fades.len() == NUM_OF_FADING_LEVELS {
            fades.pop_back();
        }

        // Add new drops.
        let mut i = 0;
        while i < NUM_OF_NEW_DROPS && digit_drops.len() < num_of_drops {
            digit_drops.push(DigitDrop::new(
                rand::thread_rng().gen_range(0..num_cols) as usize,
                0,
                num_rows as usize,
            ));
            i += 1;
        }

        screen.flush().unwrap();
        thread::sleep(time::Duration::from_millis(20));
        step += 1;
    }
}
