extern crate termion;

use std::io::{stdout, Stdout, Write};
use termion::raw::{IntoRawMode, RawTerminal};
use termion::terminal_size;

pub struct ScreenBuffer {
    pub width: usize,
    pub height: usize,
    screen: RawTerminal<Stdout>,
}

impl ScreenBuffer {
    /// Create ScreenBuffer, and clear screen.
    pub fn new() -> Self {
        let screen = stdout().into_raw_mode().unwrap();
        let (width, height) = terminal_size().unwrap();

        let mut sb = ScreenBuffer {
            width: width as usize,
            height: height as usize,
            screen: screen,
        };

        // At the beginning buffer is empty, so screen must be empty too.
        write!(sb.screen, "{}", termion::clear::All).unwrap();

        return sb;
    }

    #[allow(dead_code)]
    /// Clear screen and buffer.
    fn clear(&mut self) {
        write!(self.screen, "{}", termion::clear::All).unwrap();
    }

    #[allow(dead_code)]
    /// Send everything from buffer to screen and clear buffer.
    pub fn flush(&mut self) {
        self.screen.flush().unwrap();
    }

    /// Write text on specific position (top left cell is at position (0, 0)).
    pub fn write(&mut self, y: usize, x: usize, text: String) {
        if y >= self.height || x >= self.width {
            return;
        }

        write!(
            self.screen,
            "{}{}{}",
            termion::cursor::Hide,
            termion::cursor::Goto((x + 1) as u16, (y + 1) as u16),
            text
        )
        .unwrap();
    }
}
