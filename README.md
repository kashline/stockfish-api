# Chess Move Evaluator

This project evaluates individual chess moves by comparing them to Stockfish's best move for a given position (FEN). It returns a centipawn score difference and classifies the move (e.g., _Brilliant move_, _Blunder_, etc.).

## Features

- Evaluates player moves using Stockfish
- Scores and categorizes move quality
- Command-line testing via bash scripts

## Prerequisites

- [Docker](https://www.docker.com/)

## Project Structure

- `build.sh` – Builds and runs the API.
- `test.sh` – Sends test cases to the API and prints out the evaluation results.

## Running the Project

### Build and Start

```bash
./build.sh
```

### Test

```bash
./test.sh
```
