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

    /// Update branches based on previous warm move.
    fn update_branches(&mut self, warm: &Warm) {
        match warm.prev_dir {
            Direction::Up => self.down = true,
            Direction::Down => self.up = true,
            Direction::Left => self.right = true,
            Direction::Right => self.left = true,
        }

        match warm.dir {
            Direction::Up => self.up = true,
            Direction::Down => self.down = true,
            Direction::Left => self.left = true,
            Direction::Right => self.right = true,
        }
    }
}

/// Warm position on terminal screen.
struct Warm {
    x: usize,
    y: usize,
    prev_x: usize,
    prev_y: usize,
    dir: Direction,
    prev_dir: Direction,
}

impl Warm {
    /// Set starting position and direction for warm.
    fn new(x: usize, y: usize) -> Self {
        Warm {
            x,
            y,
            prev_x: x,
            prev_y: y,
            dir: rand::random(),
            prev_dir: rand::random(),
        }
    }

    /// Generate new direction and move warm.
    fn move_randomly(&mut self, sb: &ScreenBuffer) {
        self.prev_dir = self.dir.clone();
        self.prev_x = self.x;
        self.prev_y = self.y;

        let mut new_dir = rand::random();
        let mut is_correct = false;
        while !is_correct {
            // Change direction in case we reach wall.
            if (new_dir == Direction::Up && self.y == 0)
                || (new_dir == Direction::Down && self.y == sb.height - 1)
                || (new_dir == Direction::Left && self.x == 0)
                || (new_dir == Direction::Right && self.x == sb.width - 1)
            {
                new_dir = rand::random();
            } else {
                is_correct = true;
            }
        }

        self.dir = new_dir;
        match self.dir {
            Direction::Up => self.y -= 1,
            Direction::Down => self.y += 1,
            Direction::Left => self.x -= 1,
            Direction::Right => self.x += 1,
        }
    }
}

/// Run explorer animation.
async fn run_animation() {
    let mut sb = ScreenBuffer::new();

    let mut warm = Warm::new(sb.width / 2, sb.height / 2);
    let mut cell_map = vec![vec![Cell::new(); sb.width]; sb.height];
    cell_map[warm.y][warm.x].update_branches(&warm);

    let mut interval = tokio::time::interval(Duration::from_millis(5));
    interval.tick().await;

    loop {
        // Restore previous cell look (without warm).
        let prev_cell = &mut cell_map[warm.prev_y][warm.prev_x];
        sb.write(warm.prev_y, warm.prev_x, prev_cell.get_char().to_string());

        // Print warm in current cell
        sb.write(warm.y, warm.x, "+".to_string());
        
        // Move warm and update branches in current cell.
        let curr_cell = &mut cell_map[warm.y][warm.x];
        warm.move_randomly(&sb);
        curr_cell.update_branches(&warm);

        sb.flush();
        interval.tick().await;
    }
}

#[tokio::main]
async fn main() {
    run_animation().await;
}
