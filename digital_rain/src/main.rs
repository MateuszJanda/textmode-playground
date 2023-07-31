extern crate termion;

use rand::seq::SliceRandom;
use rand::Rng;
use std::collections::VecDeque;
use std::fmt;
use std::io::{stdout, Stdout, Write};
use termion::color::Color;
use termion::screen::{AlternateScreen, IntoAlternateScreen};
use tokio::time::Duration;

/// References:
/// - https://www.youtube.com/watch?v=F7nSAEbJGLo

/// Matrix characters.
/// - https://en.wikipedia.org/wiki/Hiragana_(Unicode_block)
/// - http://www.rikai.com/library/kanjitables/kanji_codes.unicode.shtml
const MATRIX_CHARS: [char; 91] = [
    'ぁ', 'あ', 'ぃ', 'い', 'ぅ', 'う', 'ぇ', 'え', 'ぉ', 'お', 'か', 'が', 'き', 'ぎ', 'く', 'ぐ',
    'け', 'げ', 'こ', 'ご', 'さ', 'ざ', 'し', 'じ', 'す', 'ず', 'せ', 'ぜ', 'そ', 'ぞ', 'た', 'だ',
    'ち', 'ぢ', 'っ', 'つ', 'づ', 'て', 'で', 'と', 'ど', 'な', 'に', 'ぬ', 'ね', 'の', 'は', 'ば',
    'ぱ', 'ひ', 'び', 'ぴ', 'ふ', 'ぶ', 'ぷ', 'へ', 'べ', 'ぺ', 'ほ', 'ぼ', 'ぽ', 'ま', 'み', 'む',
    'め', 'も', 'ゃ', 'や', 'ゅ', 'ゆ', 'ょ', 'よ', 'ら', 'り', 'る', 'れ', 'ろ', 'ゎ', 'わ', 'ゐ',
    'ゑ', 'を', 'ん', 'ゔ', 'ゕ', 'ゖ', '゛', '゜', 'ゝ', 'ゞ', 'ゟ',
];

const NUM_OF_INIT_DROPS: usize = 40;
const NUM_OF_NEW_DROPS: usize = 10;
const NUM_OF_FADING_LEVELS: usize = 16;
/// Number of drops = width * height * DROPS_ON_SCREEN_FACTOR
const DROPS_ON_SCREEN_FACTOR: f32 = 0.06;
/// Hiragana characters occupy two normal characters widths.
const CHAR_WIDTH: usize = 2;
const DELAY_IN_MS: u64 = 20;

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
            _ => "\x1B[38;2;0;0;0m",
        }
    }

    /// Returns the ANSI escape sequences for background RGB color (black) as a string (&'static str).
    #[inline]
    pub fn bg_str(&self) -> &'static str {
        // csi!("48;2;", $value, "m")
        "\x1B[48;2;0;0;0m"
    }
}

#[derive(Clone, Debug)]
struct DigitDrop {
    x: usize,
    y: usize,
    height: usize,
    ch: char,
    speed_step: u32,
    new_char_step: u32,
}

impl DigitDrop {
    fn new(x: usize, y: usize, height: usize) -> Self {
        DigitDrop {
            x,
            y,
            height,
            ch: *MATRIX_CHARS.choose(&mut rand::thread_rng()).unwrap(),
            speed_step: rand::thread_rng().gen_range(1..6),
            new_char_step: rand::thread_rng().gen_range(1..10),
        }
    }

    /// Print drop and fading to buffer.
    fn print(&self, buffer: &mut Vec<Vec<String>>, fade_level: usize) {
        if self.y >= buffer.len() {
            return;
        }

        // ANSI position (used by Goto) start from one.
        buffer[self.y][self.x] = match fade_level {
            // If this is last fading phase then clear character (two space because Hiragana occupy
            // two normal width) on screen.
            NUM_OF_FADING_LEVELS => format!("{}  ", termion::color::Fg(FadeColor(0))),
            _ => format!("{}{}", termion::color::Fg(FadeColor(fade_level)), self.ch),
        }
    }

    /// Move drop down but only if current "step" match "speed_step" or choose new character if
    /// "step" match "new_char_step".
    fn action(&mut self, step: u32) {
        if step % self.speed_step == 0 {
            self.y += 1;
        }

        if step % self.new_char_step == 0 {
            self.ch = *MATRIX_CHARS.choose(&mut rand::thread_rng()).unwrap();
        }
    }

    /// Check if drop if out of the screen.
    fn is_out_of_screen(&self) -> bool {
        self.y >= self.height
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

#[tokio::main]
async fn main() {
    // Init screen.
    let mut screen: AlternateScreen<Stdout> = stdout().into_alternate_screen().unwrap();
    init_screen(&mut screen);

    // Get terminal size
    let (num_cols, num_rows) = termion::terminal_size().unwrap();
    let num_of_drops: usize = ((num_cols * num_rows) as f32 * DROPS_ON_SCREEN_FACTOR) as usize;
    let height = num_rows as usize;
    let width = num_cols as usize / CHAR_WIDTH;

    // Init data
    let mut buffer: Vec<Vec<String>> = vec![vec!["  ".into(); width]; height];
    let mut fades: VecDeque<Vec<DigitDrop>> = VecDeque::new();
    let mut digit_drops: Vec<DigitDrop> = vec![];

    // Add few characters at the start.
    for _ in 0..NUM_OF_INIT_DROPS {
        digit_drops.push(DigitDrop::new(
            rand::thread_rng().gen_range(0..width),
            0,
            height,
        ));
    }

    let mut step = 1;
    let mut interval = tokio::time::interval(Duration::from_millis(DELAY_IN_MS));
    interval.tick().await;
    loop {
        // Print fading drops into buffer.
        for (fade_level, drops) in fades.iter().enumerate() {
            for fade_drop in drops.iter() {
                fade_drop.print(&mut buffer, fade_level + 1);
            }
        }

        // Trigger all drops to check if the should be moved or not.
        let mut fading_drops: Vec<DigitDrop> = vec![];
        for digit_drop in digit_drops.iter_mut() {
            fading_drops.push(digit_drop.clone());
            digit_drop.action(step);
            digit_drop.print(&mut buffer, 0);
        }

        // Draw on screen line by line.
        for (y, row) in buffer.iter().enumerate() {
            write!(
                screen,
                "{}{}",
                termion::cursor::Goto(1, y as u16 + 1),
                row.join("")
            )
            .unwrap();
        }

        // Update. Digital drops will fade from this point.
        fades.push_front(fading_drops);

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
                rand::thread_rng().gen_range(0..width),
                0,
                height,
            ));
            i += 1;
        }

        interval.tick().await;
        screen.flush().unwrap();
        step += 1;
    }
}
