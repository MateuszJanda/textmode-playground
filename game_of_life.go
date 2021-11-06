// Author: Mateusz Janda <mateusz janda at gmail com>
// Site: github.com/MateuszJanda/textmode-playground
// Ad maiorem Dei gloriam

package main

import (
	"fmt"
	"log"
	"os"
	"os/exec"
	"strconv"
	"strings"
	"time"
)

func main() {
	clearScreen()
	width, height := getTerminalSize()

	oldBoard := makeBoard(height, width)
	initBoardWithAcorn(&oldBoard)
	printBoard(oldBoard)

	const ROUNDS = 1000
	for i := 0; i < ROUNDS; i++ {
		time.Sleep(100 * time.Millisecond)
		newBoard := gameOfLifeRound(oldBoard)
		printBoard(newBoard)
		oldBoard = newBoard
	}
}

func clearScreen() {
	cmd := exec.Command("clear")
	cmd.Stdout = os.Stdout
	cmd.Run()
}

func getTerminalSize() (int, int) {
	cmd := exec.Command("stty", "size")
	cmd.Stdin = os.Stdin
	out, err := cmd.Output()
	if err != nil {
		log.Fatal(err)
	}

	size := strings.Split(string(out), " ")
	height, err := strconv.Atoi(strings.TrimSpace(size[0]))
	if err != nil {
		log.Fatal(err)
	}

	width, err := strconv.Atoi(strings.TrimSpace(size[1]))
	if err != nil {
		log.Fatal(err)
	}

	return width, height
}

func makeBoard(height int, width int) [][]int {
	newBoard := make([][]int, height)
	for y := range newBoard {
		newBoard[y] = make([]int, width)
	}
	return newBoard
}

func initBoardWithBlinker(board *[][]int) {
	height := len(*board)
	width := len((*board)[0])

	// Set pattern: blinker
	(*board)[height/2-1][width/2] = 1
	(*board)[height/2][width/2] = 1
	(*board)[height/2+1][width/2] = 1
}

func initBoardWithDiehard(board *[][]int) {
	height := len(*board)
	width := len((*board)[0])

	// Set pattern: diehard
	(*board)[height/2-1][width/2] = 1

	(*board)[height/2-1][width/2+1] = 1
	(*board)[height/2][width/2+1] = 1

	(*board)[height/2][width/2+5] = 1

	(*board)[height/2][width/2+6] = 1
	(*board)[height/2-2][width/2+6] = 1

	(*board)[height/2][width/2+7] = 1
}

func initBoardWithAcorn(board *[][]int) {
	height := len(*board)
	width := len((*board)[0])

	// Set pattern: acorn
	(*board)[height/2][width/2] = 1

	(*board)[height/2][width/2+1] = 1
	(*board)[height/2-2][width/2+1] = 1

	(*board)[height/2-1][width/2+3] = 1

	(*board)[height/2][width/2+4] = 1
	(*board)[height/2][width/2+5] = 1
	(*board)[height/2][width/2+6] = 1
}

func gameOfLifeRound(oldBoard [][]int) [][]int {
	height := len(oldBoard)
	width := len(oldBoard[0])

	// Counte neighbours
	neighboursCount := makeBoard(height, width)
	update := func(y int, x int) {
		if y >= 0 && y < height && x >= 0 && x < width {
			neighboursCount[y][x] += 1
		}
	}

	for y := 0; y < height; y++ {
		for x := 0; x < width; x++ {
			if oldBoard[y][x] != 1 {
				continue
			}

			update(y-1, x-1)
			update(y-1, x)
			update(y-1, x+1)

			update(y, x-1)
			update(y, x+1)

			update(y+1, x-1)
			update(y+1, x)
			update(y+1, x+1)
		}
	}

	// Game rules
	newBoard := makeBoard(height, width)

	for y := 0; y < height; y++ {
		for x := 0; x < width; x++ {
			if oldBoard[y][x] <= 0 && neighboursCount[y][x] == 3 {
				// Any dead cell with three live neighbours becomes a live cell
				newBoard[y][x] = 1
			} else if oldBoard[y][x] > 0 && (neighboursCount[y][x] == 2 || neighboursCount[y][x] == 3) {
				// Any live cell with two or three live neighbours survives
				newBoard[y][x] = 1
			} else if oldBoard[y][x] > 0 {
				// All other live cells die in the next generation
				newBoard[y][x] = -1
			} else if oldBoard[y][x] < 0 {
				// All other dead cells stay dead
				newBoard[y][x] = 0
			}
		}
	}

	return newBoard
}

func printBoard(board [][]int) {
	height := len(board)
	width := len(board[0])

	// https://en.wikipedia.org/wiki/Geometric_Shapes
	for y := 0; y < height; y++ {
		for x := 0; x < width; x++ {
			val := board[y][x]
			char := " "
			switch val {
			case -1:
				// char = "▫"
			case 1:
				// char = "▪"
				char = "1"
				// char = "◼"
			default:
				char = " "
			}

			fmt.Fprintf(os.Stdout, "\033[%d;%dH%s", y, x, char)
		}
	}
}

func debugBoard(board [][]int) {
	height := len(board)
	width := len((board)[0])

	for y := 0; y < height; y++ {
		for x := 0; x < width; x++ {
			if board[y][x] >= 0 {
				fmt.Print(board[y][x])
			} else {
				fmt.Print("-")
			}
		}
		fmt.Println()
	}
	fmt.Println()
}
