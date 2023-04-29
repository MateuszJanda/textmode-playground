extern crate termion;

use std::io::{stdout, Stdout, Write};
use termion::raw::{IntoRawMode, RawTerminal};
use termion::terminal_size;

pub struct ScreenBuffer {
    pub width: u16,
    pub height: u16,
    screen: RawTerminal<Stdout>,
}

impl ScreenBuffer {
    /// Create ScreenBuffer, and clear screen.
    pub fn new() -> ScreenBuffer {
        let mut screen = stdout().into_raw_mode().unwrap();
        let (width, height) = terminal_size().unwrap();

        let mut sb = ScreenBuffer {
            width: width as u16,
            height: height as u16,
            screen: screen,
        };

        // At the beginning buffer is empty, so screen must be empty too.
        write!(sb.screen, "{}", termion::clear::All).unwrap();

        return sb;
    }

    /// Clear screen and buffer.
    fn clear(mut self) {
        write!(self.screen, "{}", termion::clear::All).unwrap();
    }

    /// Send everything from buffer to screen and clear buffer.
    fn flush(mut self) {
        // self.screen.flush().unwrap();
    }

    /// Write text on specific position (numeration start from 1).
    pub fn write(&mut self, y: u16, x: u16, text: String) {
        if y == 0 || x == 0 {
            return;
        }

        write!(
            self.screen,
            "{}{}{}",
            termion::cursor::Hide,
            termion::cursor::Goto(y, x),
            text
        )
        .unwrap();
    }
}
