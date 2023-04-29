use explorer::ScreenBuffer;
use tokio::time::Duration;

#[tokio::main]
async fn main() {
    run_animation().await;
}       

/// Run explorer animation.
/// https://en.wikipedia.org/wiki/Box_Drawing
async fn run_animation() {
    let mut sb = ScreenBuffer::new();
    let (start_y, start_x) = (sb.width / 2, sb.height / 2);
    let mut interval = tokio::time::interval(Duration::from_millis(100));

    interval.tick().await;
    loop {
        sb.write(start_y, start_x, "├".to_string());
        interval.tick().await;
    }
}
