extern crate termion;

use rand::distributions::Alphanumeric;
use rand::Rng;
use std::collections::VecDeque;
use std::fmt;
use std::io::{stdout, Stdout, Write};
use std::{thread, time};
use termion::color::Color;
use termion::screen::{AlternateScreen, IntoAlternateScreen};

const NUM_OF_DROPS: usize = 80;
const NUM_OF_NEW_DROPS: usize = 10;
const NUM_OF_FADING_LEVELS: usize = 9;
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
    /// Returns the ANSI escape sequence for foreground color (RGB) as a string (&'static str).
    pub fn fg_str(&self) -> &'static str {
        // csi!("38;2;", $value, "m")
        match self.0 {
            0 => "\x1B[38;2;0;255;0m",
            1 => "\x1B[38;2;0;225;0m",
            // 1 => "\x1B[38;2;255;225;0m",
            2 => "\x1B[38;2;0;205;0m",
            // 2 => "\x1B[38;2;0;205;255m",
            3 => "\x1B[38;2;0;185;0m",
            // 3 => "\x1B[38;2;0;0;255m",
            4 => "\x1B[38;2;0;165;0m",
            5 => "\x1B[38;2;0;145;0m",
            6 => "\x1B[38;2;0;125;0m",
            7 => "\x1B[38;2;0;105;0m",
            8 => "\x1B[38;2;0;85;0m",
            9 => "\x1B[38;2;0;65;0m",
            10 => "\x1B[38;2;0;45;0m",
            11 => "\x1B[38;2;0;25;0m",
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
    num_rows: usize,
    x: usize,
    y: usize,
    ch: char,
    speed_step: u32,
}

impl DigitDrop {
    fn new(x: usize, y: usize, buffer: &mut Vec<Vec<char>>) -> Self {
        let ch = rand::thread_rng().sample(Alphanumeric) as char;
        buffer[y][x] = ch;
        DigitDrop {
            num_rows: buffer.len(),
            x,
            y,
            ch,
            speed_step: rand::thread_rng().gen_range(1..10),
            // speed_step: 3,
        }
    }

    /// Print digital drop.
    fn print_drop(&self, screen: &mut AlternateScreen<Stdout>, buffer: &mut Vec<Vec<char>>) {
        if self.y >= buffer.len() {
            return;
        }

        buffer[self.y][self.x] = self.ch;
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
    fn print_fade(
        &self,
        screen: &mut AlternateScreen<Stdout>,
        buffer: &mut Vec<Vec<char>>,
        fade_level: usize,
    ) {
        // ANSI position (used by Goto) start from one.
        match fade_level {
            // If this is last fading phase then clear character on screen.
            NUM_OF_FADING_LEVELS => {
                write!(
                    screen,
                    "{} ",
                    termion::cursor::Goto(self.x as u16 + 1, self.y as u16 + 1),
                )
                .unwrap();
                // buffer[self.y][self.x] = ' ';
            }
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
    fn go_down(&mut self, buffer: &mut Vec<Vec<char>>, step: u32) -> Option<DigitDrop> {
        // Check if drop should fall in this step.
        if step % self.speed_step != 0 {
            return None;
        }

        let prev = self.clone();
        self.y += 1;
        if self.y < buffer.len() {
            buffer[self.y][self.x] = self.ch;
        }

        return Some(prev);
    }

    /// Check if character in buffer and "digit drop" character at same position are same.
    fn is_in_buffer(&self, buffer: &Vec<Vec<char>>) -> bool {
        if self.y < buffer.len() {
            return buffer[self.y][self.x] == self.ch;
        }

        false
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

    // Init data
    let mut buffer: Vec<Vec<char>> = vec![vec![' '; num_cols as usize]; num_rows as usize];
    let mut fades: VecDeque<Vec<DigitDrop>> = VecDeque::new();
    let mut digit_drops: Vec<DigitDrop> = vec![];

    // for x in 0..num_cols as usize {
    //     if rand::thread_rng().gen_range(0..100) < INIT_DROPS_PROB {
    //         digit_drops.push(DigitDrop::new(x, 0, num_rows as usize));
    //     }
    // }

    // for _ in 0..30 {
    //     digit_drops.push(DigitDrop::new(
    //         rand::thread_rng().gen_range(0..num_cols) as usize,
    //         0,
    //         &mut buffer,
    //     ));
    // }

    digit_drops.push(DigitDrop::new(1, 0, &mut buffer));
    // digit_drops.push(DigitDrop::new(3, 0, num_rows as usize));
    // buffer[0][1] = 'x';

    // for digit_drop in digit_drops.iter() {
    //     buffer[digit_drop.y][digit_drop.x] = digit_drop.ch;
    // }

    let mut step = 1;
    loop {
        // Trigger all drops to check if the should be moved or not.
        let mut fading_drops: Vec<DigitDrop> = vec![];
        for digit_drop in digit_drops.iter_mut() {
            fading_drops.push(digit_drop.clone());

            if let Some(prev) = digit_drop.go_down(&mut buffer, step) {
                digit_drop.print_drop(&mut screen, &mut buffer);
            }
        }

        // Update. Digital drops will fade from this point.
        fades.push_front(fading_drops);

        // // Draw digital drops.
        // for digit_drop in digit_drops.iter() {
        //     digit_drop.print_drop(&mut screen);
        // }

        // Draw fading drops.
        for (fade_level, drops) in fades.iter().enumerate() {
            for fade_drop in drops.iter() {
                fade_drop.print_fade(&mut screen, &mut buffer, fade_level + 1);
            }
        }

        // Remove all drops that are out of the screen.
        digit_drops.retain(|digit_drop| !digit_drop.is_out_of_screen());

        // Removed overlapping drop fading with real digital drop.
        // for fading_drops in fades.iter_mut() {
        //     fading_drops.retain(|fade_drop: &DigitDrop| fade_drop.is_in_buffer(&buffer));
        // }

        // Remove last fading
        if fades.len() == NUM_OF_FADING_LEVELS {
            fades.pop_back();
        }

        // Add new drops.
        let mut i = 0;
        while i < NUM_OF_NEW_DROPS && digit_drops.len() < NUM_OF_DROPS {
            digit_drops.push(DigitDrop::new(
                rand::thread_rng().gen_range(0..num_cols) as usize,
                // 5,
                0,
                &mut buffer,
            ));
            i += 1;
        }

        screen.flush().unwrap();
        thread::sleep(time::Duration::from_millis(20));
        step += 1;
    }
}
