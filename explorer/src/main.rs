use explorer::ScreenBuffer;
use rand::distributions::{Distribution, Standard};
use rand::Rng;
use tokio::time::Duration;

#[derive(PartialEq, Eq, Clone, Debug)]
/// Warm direction.
enum Direction {
    Up,
    Down,
    Left,
    Right,
}

impl Distribution<Direction> for Standard {
    /// To generate random Direction.
    ///
    /// # Example:
    /// ```
    /// let dir: Direction = rand::random();
    /// ```
    fn sample<R: Rng + ?Sized>(&self, rng: &mut R) -> Direction {
        match rng.gen_range(0..=3) {
            0 => Direction::Up,
            1 => Direction::Down,
            2 => Direction::Left,
            _ => Direction::Right,
        }
    }
}

#[derive(PartialEq, Eq, Clone, Debug)]
/// Cell represent one char on terminal screen and char is "Box block" with four branches.
///
/// # See also:
/// * https://en.wikipedia.org/wiki/Box_Drawing
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
    fn set_random_direction(&mut self, old_dir: Option<Direction>) -> Direction {
        if let Some(dir) = old_dir {
            match dir {
                Direction::Up => self.down = true,
                Direction::Down => self.up = true,
                Direction::Left => self.right = true,
                Direction::Right => self.left = true,
            }
        }

        let new_dir: Direction = rand::random();
        match new_dir {
            Direction::Up => self.up = true,
            Direction::Down => self.down = true,
            Direction::Left => self.left = true,
            Direction::Right => self.right = true,
        }

        new_dir
    }
}

/// Warm position on terminal screen.
struct Warm {
    x: usize,
    y: usize,
}

impl Warm {
    /// Set stating position for warm.
    fn new(x: usize, y: usize) -> Self {
        Warm { x, y }
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
            new_dir = rand::random();
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
