from flask import Flask, request, jsonify
import subprocess
import logging

# Set up basic logging configuration
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
stockfish_path = "/opt/Stockfish/src/stockfish"

def run_stockfish(commands: list[str]) -> list[str]:
    process = subprocess.Popen(
        [stockfish_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1  # line buffered
    )

    output_lines = []

    for command in commands:
        process.stdin.write(command + "\n")
        process.stdin.flush()

    # Read until we see "bestmove"
    while True:
        line = process.stdout.readline()
        if line == '':
            break  # Process terminated or pipe closed unexpectedly
        line = line.strip()
        if line:
            output_lines.append(line)
            if line.startswith("bestmove"):
                break  # We've got the final result

    # Now quit Stockfish nicely
    process.stdin.write("quit\n")
    process.stdin.flush()
    process.wait()

    return output_lines

@app.route('/')
def index():
    return "Flask is working!"

@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.get_json()
    moves = data.get("moves", "")
    depth = data.get("depth", 15)

    cmds = [
        "uci",
        "isready",
        f"position startpos moves {moves}",
        f"go depth {depth}"
    ]
    output = run_stockfish(cmds)
    return jsonify({"output": output})

@app.route('/evaluatemove', methods=['POST'])
def evaluate_move():
    data = request.get_json()

    fen = data.get('fen')
    move = data.get('move')

    if not fen or not move:
        return jsonify({"error": "Missing 'fen' or 'move' in request"}), 400

    # Commands for Stockfish to get the best move and evaluation
    commands = [
        "uci",
        "isready",
        "setoption name MultiPV value 1",
        f"position fen {fen}",
        "go depth 20"
    ]

    # Run Stockfish and capture the output
    stockfish_output = run_stockfish(commands)
    best_move = None
    best_score = None

    # Parse the output to get best move and evaluation
    for line in stockfish_output:
        if line.startswith("bestmove"):
            best_move = line.split()[1]
        if line.startswith("info"):
            if "score" in line:
                # Extract centipawn score if available
                if "cp" in line:
                    best_score = int(line.split("score cp")[1].split()[0])
                # Extract mate score if available
                elif "mate" in line:
                    best_score = int(line.split("score mate")[1].split()[0])
    # Evaluate the player's move
    commands = [
        "uci", 
        "isready", 
        f"position fen {fen} moves {move}",  # Add player's move
        "go depth 20"
    ]
    player_output = run_stockfish(commands)

    player_score = None
    for line in player_output:
        if line.startswith("info"):
            if "score" in line:
                # Extract centipawn score if available
                if "cp" in line:
                    player_score = int(line.split("score cp")[1].split()[0])
                # Extract mate score if available
                elif "mate" in line:
                    player_score = int(line.split("score mate")[1].split()[0])
    # Default to zero if no valid score was found
    best_score = best_score if best_score is not None else 0
    player_score = player_score if player_score is not None else 0
    # Calculate the score difference
    score_diff = abs(best_score - player_score)

    # Classify the move
    if score_diff <= 20:
        rating = "Brilliant move"
    elif score_diff <= 50:
        rating = "Great move"
    elif score_diff <= 100:
        rating = "Good move"
    elif score_diff <= 200:
        rating = "Inaccuracy"
    elif score_diff <= 400:
        rating = "Mistake"
    else:
        rating = "Blunder"

    return jsonify({
        "player_move": move,
        "best_move": best_move,
        "score_difference": score_diff,
        "rating": rating
    })

def parse_bestmove(output: str) -> str:
    for line in output.splitlines():
        if line.startswith("bestmove"):
            return line.split()[1]
    return ""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

