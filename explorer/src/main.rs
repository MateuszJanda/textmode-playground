use explorer::ScreenBuffer;
use rand::Rng;
use tokio::time::Duration;

#[derive(PartialEq, Eq, Clone, Debug)]
enum Direction {
    Up,
    Down,
    Left,
    Right,
}

#[derive(PartialEq, Eq, Clone, Debug)]
struct Cell {
    up: bool,
    down: bool,
    left: bool,
    right: bool,
}

impl Cell {
    /// Create new cell with all branches set to false what is equal to ' '.
    fn new() -> Self {
        Cell {
            up: false,
            down: false,
            left: false,
            right: false,
        }
    }

    /// Get char based on cell settings.
    /// https://en.wikipedia.org/wiki/Box_Drawing
    fn get_char(&self) -> char {
        match (self.up, self.down, self.left, self.right) {
            (false, false, false, false) => ' ',
            (false, false, false, true) => '╶',
            (false, false, true, false) => '╴',
            (false, false, true, true) => '─',
            (false, true, false, false) => '╷',
            (false, true, false, true) => '┌',
            (false, true, true, false) => '┐',
            (false, true, true, true) => '┬',
            (true, false, false, false) => '╵',
            (true, false, false, true) => '└',
            (true, false, true, false) => '┘',
            (true, false, true, true) => '┴',
            (true, true, false, false) => '│',
            (true, true, false, true) => '├',
            (true, true, true, false) => '┤',
            (true, true, true, true) => '┼',
        }
    }

    /// Set random direction based on previous cell direction.
    fn set_random_direction(&mut self, dir: Option<Direction>) -> Direction {
        if let Some(d) = dir {
            match d {
                Direction::Up => self.down = true,
                Direction::Down => self.up = true,
                Direction::Left => self.right = true,
                Direction::Right => self.left = true,
            }
        }

        match rand::thread_rng().gen_range(0..4) {
            0 => {
                self.up = true;
                Direction::Up
            }
            1 => {
                self.down = true;
                Direction::Down
            }
            2 => {
                self.left = true;
                Direction::Left
            }
            _ => {
                self.right = true;
                Direction::Right
            }
        }
    }
}

/// Generate new direction.
fn new_direction() -> Direction {
    match rand::thread_rng().gen_range(0..4) {
        0 => Direction::Up,
        1 => Direction::Down,
        2 => Direction::Left,
        _ => Direction::Right,
    }
}

fn fix_direction(
    height: usize,
    width: usize,
    mut dir: Direction,
    pos_y: usize,
    pos_x: usize,
) -> Direction {
    let mut is_correct = false;
    while !is_correct {
        if (dir == Direction::Up && pos_y == 0)
            || (dir == Direction::Down && pos_y == height - 1)
            || (dir == Direction::Left && pos_x == 0)
            || (dir == Direction::Right && pos_x == width - 1)
        {
            dir = new_direction();
        } else {
            is_correct = true;
        }
    }

    dir
}

/// Run explorer animation.
async fn run_animation() {
    let mut sb = ScreenBuffer::new();
    let mut cell_map = vec![vec![Cell::new(); sb.width]; sb.height];
    let (mut pos_y, mut pos_x) = (sb.height / 2, sb.width / 2);
    let mut dir = None;

    let mut interval = tokio::time::interval(Duration::from_millis(5));
    interval.tick().await;

    loop {
        let new_dir = cell_map[pos_y][pos_x].set_random_direction(dir);
        sb.write(pos_y, pos_x, cell_map[pos_y][pos_x].get_char().to_string());

        let new_dir = fix_direction(sb.height as usize, sb.width as usize, new_dir, pos_y, pos_x);
        match new_dir {
            Direction::Up => pos_y -= 1,
            Direction::Down => pos_y += 1,
            Direction::Left => pos_x -= 1,
            Direction::Right => pos_x += 1,
        }
        dir = Some(new_dir);

        sb.flush();
        interval.tick().await;
    }
}

#[tokio::main]
async fn main() {
    run_animation().await;
}
