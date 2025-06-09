from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import logging

# Set up basic logging configuration
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)
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

def run_stockfish_unfil(commands: list[str], terminator: str) -> list[str]:
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
    while True:
        line = process.stdout.readline()
        if line == '':
            break  # Process terminated or pipe closed unexpectedly
        line = line.strip()
        if line:
            output_lines.append(line)
        if terminator in line:
            break 

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

@app.route('/legal_moves', methods=['POST'])
def legal_moves():
    data = request.get_json()
    fen = data.get("fen", "")
    cmds = [
        "uci",
        "isready",
        f"position fen {fen}",
        "go perft 1"
    ]
    output = run_stockfish_unfil(cmds, "Nodes searched:")

    return jsonify({"legal_moves": extract_moves(output)})

@app.route('/makemove', methods=['POST'])
def make_move():
    data = request.get_json()
    fen = data.get('fen')
    if not fen:
        return jsonify({"error": "Missing 'fen' in request"}), 400
    
    commands = [
        "uci",
        "isready",
        "setoption name MultiPV value 1",
        f"position fen {fen}",
        "go depth 20"
    ]
    stockfish_output = run_stockfish(commands)
    best_move = None

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
    return jsonify({
        "best_move": best_move,
    })


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
    elif score_diff <= 999:
        rating = "Blunder"
    else:
        rating = "CRITICAL BLUNDER"

    return jsonify({
        "player_move": move,
        "best_move": best_move,
        "score_difference": score_diff,
        "rating": rating
    })

def extract_moves(lines):
    moves = []
    for line in lines:
        # Check if line contains ':' and looks like a move (4 characters before ':')
        if ":" in line:
            move_part = line.split(":")[0]
            # Move should start with a letter and be exactly 4 characters long (e.g., 'e2e4')
            if move_part[0].isalpha() and len(move_part) == 4:
                moves.append(move_part)
    return moves

def parse_bestmove(output: str) -> str:
    for line in output.splitlines():
        if line.startswith("bestmove"):
            return line.split()[1]
    return ""

@app.route("/move", methods=["POST"])
def move():
    data = request.json
    fen = data.get("fen")
    move = data.get("move")

    if not fen or not move:
        return jsonify({"error": "Missing FEN or move"}), 400
    try:
        commands = [
            "uci",
            "isready",
            f"position fen {fen} moves {move}",
            "d"
        ]

        output = run_stockfish_unfil(commands, "Checkers:")
        new_fen = None
        for line in output:
            if line.startswith("Fen: "):
                new_fen = line.removeprefix("Fen: ").strip()
                break

        if not new_fen:
            return jsonify({"error": "FEN not found in Stockfish output"}), 500
        return jsonify({"fen": new_fen})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

