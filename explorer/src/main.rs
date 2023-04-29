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

struct Warm {
    x: usize,
    y: usize,
}

impl Warm {
    fn new(x: usize, y: usize) -> Self {
        Warm { x, y }
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

/// Change direction in case we reach wall.
fn fix_direction(sb: &ScreenBuffer, mut new_dir: Direction, warm: &Warm) -> Direction {
    let mut is_correct = false;
    while !is_correct {
        if (new_dir == Direction::Up && warm.y == 0)
            || (new_dir == Direction::Down && warm.y == sb.height - 1)
            || (new_dir == Direction::Left && warm.x == 0)
            || (new_dir == Direction::Right && warm.x == sb.width - 1)
        {
            new_dir = new_direction();
        } else {
            is_correct = true;
        }
    }

    new_dir
}

/// Run explorer animation.
async fn run_animation() {
    let mut sb = ScreenBuffer::new();
    let mut cell_map = vec![vec![Cell::new(); sb.width]; sb.height];
    let mut warm = Warm::new(sb.width / 2, sb.height / 2);
    let mut dir = None;

    let mut interval = tokio::time::interval(Duration::from_millis(5));
    interval.tick().await;

    loop {
        let new_dir = cell_map[warm.y][warm.x].set_random_direction(dir);
        sb.write(
            warm.y,
            warm.x,
            cell_map[warm.y][warm.x].get_char().to_string(),
        );

        let new_dir = fix_direction(&sb, new_dir, &warm);
        match new_dir {
            Direction::Up => warm.y -= 1,
            Direction::Down => warm.y += 1,
            Direction::Left => warm.x -= 1,
            Direction::Right => warm.x += 1,
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
