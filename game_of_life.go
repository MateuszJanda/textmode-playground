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
	initBoard(&oldBoard)
	printBoard(oldBoard)

	const ROUNDS = 1000
	for i := 0; i < ROUNDS; i++ {
		time.Sleep(1000 * time.Millisecond)
		newBoard := gameOfLifeRound(oldBoard)
		printBoard(newBoard)
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

func initBoard(board *[][]int) {
	height := len(*board)
	width := len((*board)[0])

	// Set pattern: acorn
	(*board)[height/2][width/2] = 1
	(*board)[height/2][width/2+1] = 1
	(*board)[height/2-2][width/2+1] = 1

	(*board)[height/2-1][width/2+3] = 1
	(*board)[height/2-1][width/2+4] = 1
	(*board)[height/2-1][width/2+5] = 1
	(*board)[height/2-1][width/2+6] = 1
}

func copyBoard(board [][]int) [][]int {
	duplicate := make([][]int, len(board))
	for y := range board {
		duplicate[y] = make([]int, len(board[y]))
		copy(duplicate[y], board[y])
	}

	return duplicate
}

func gameOfLifeRound(oldBoard [][]int) [][]int {
	newBoard := copyBoard(oldBoard)

	height := len(oldBoard)
	width := len(oldBoard[0])

	for y := 0; y < height; y++ {
		for x := 0; x < width; x++ {
			neighboursCount := 0

			// Count neighbours
			for yy := y - 1; yy <= y+1; yy++ {
				for xx := x - 1; xx <= x+1; xx++ {
					if yy < 0 || yy >= height || xx < 0 || xx >= width {
						continue
					}

					if oldBoard[yy][xx] > 0 {
						neighboursCount++
					}
				}
			}

			// Game rules
			if oldBoard[y][x] <= 0 && neighboursCount == 3 {
				// Any dead cell with three live neighbours becomes a live cell
				newBoard[y][x] = 1
			} else if oldBoard[y][x] > 0 && (neighboursCount == 2 || neighboursCount == 3) {
				// Any live cell with two or three live neighbours survives
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
				char = "▫"
			case 1:
				char = "▪"
			default:
				char = " "
			}

			fmt.Printf("\033[%d;%dH%s", y, x, char)
		}
	}
}
