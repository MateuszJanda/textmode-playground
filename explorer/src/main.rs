use std::io::Read;

fn main() {
    // https://en.wikipedia.org/wiki/Box_Drawing
    // println!("Hello, world!");

    // Get width and height
    // print!("\e[18t");

    // Clear screen
    // print!("\\033[2J");

    // print!("\033c"); print!("\033[A");


    // https://en.wikipedia.org/wiki/ANSI_escape_code
    // println!("\x1b[0;31mSO\x1b[0m");



    // Get width and height
    println!("\x1b[18t");

    use std::io::{stdin,stdout,Write};

    let mut s=String::new();

    stdin().read_line(&mut s).expect("Did not enter a correct string");
    // stdin().read(&mut s).expect("Did not enter a correct string");
    // stdin().read_to_s    tring(&mut s).expect("Did not enter a correct string");

    if let Some('\n')=s.chars().next_back() {
        s.pop();
    }
    if let Some('\r')=s.chars().next_back() {
        s.pop();
    }
    println!("You typed: {}",s);

    // Clear screen
    // println!("\x1b[2J");
    // println!("\x1bc\x1b[2J");


}
