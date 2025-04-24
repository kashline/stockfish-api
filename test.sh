#!/bin/bash

API_URL="localhost:5001/evaluatemove"
test_cases=(
    "rnbqkbnr/ppp2ppp/8/3p4/4P3/8/PPP2PPP/RNBQKBNR b KQkq - 0 1 d5d4"
    "rnbqkbnr/ppp2ppp/8/3p4/4P3/8/PPP2PPP/RNBQKBNR w KQkq - 0 1 g1f3"
    "rnbqkbnr/pppppppp/8/8/8/8/PPP1PPPP/RNBQKBNR w KQkq - 0 1 e2e4"
    "rnbqkbnr/pppppppp/8/8/8/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1 e7e5"
    "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 2 4 b1c3"
    "rnbqkbnr/pppp1ppp/8/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR b KQkq - 2 2 g8f6"
    "r1bq1rk1/pppp1ppp/2n2n2/2b1p3/2B1P3/2P2N2/PP1P1PPP/RNBQ1RK1 w - - 6 6 d2d4"
    "rnbqkbnr/ppp2ppp/8/3pp3/3PP3/8/PPP2PPP/RNBQKBNR w KQkq d6 0 3 d4e5"
    "r1bqkbnr/pppp1ppp/2n5/4p3/3PP3/8/PPP2PPP/RNBQKBNR b KQkq - 0 3 e5d4"
    "r2qk2r/ppp2ppp/2np1n2/4p3/4P3/2P2N2/PP1P1PPP/R1BQ1RK1 b kq - 2 7 c8g4"
    "r1bqkbnr/pppp1ppp/2n5/4p3/2BPP3/8/PPP2PPP/RNBQK1NR b KQkq d3 0 3 e5d4"
    "r1bqkbnr/pppp1ppp/2n5/4p3/1PB1P3/8/P1P2PPP/RNBQK1NR b KQkq - 0 3 a7a5"
    "rnbqkbnr/pppp1ppp/8/4p3/1PB1P3/8/P1P2PPP/RNBQK1NR w KQkq - 0 3 c4f7"
    "r1bqkbnr/ppp2ppp/2n5/3pp3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq d6 0 4 e4d5"
    "rnbqkbnr/pppp1ppp/8/4p3/1PB1P3/8/P1P2PPP/RNBQK1NR b KQkq - 0 3 f8b4"
    "r1bqk1nr/pppp1ppp/2n5/4p3/1PB1P3/5N2/P1P2PPP/RNBQ1RK1 w kq - 2 5 c4f7"
    "r2q1rk1/ppp2ppp/2npbn2/4p3/4P3/2P2N2/PP1P1PPP/RNBQR1K1 w - - 4 8 d2d4"
    "r1bqkbnr/ppp2ppp/2n5/3pp3/3PP3/5N2/PPP2PPP/RNBQKB1R w KQkq d6 0 4 e4d5"
    "r1bqkbnr/ppp2ppp/2n5/3pp3/3PP3/5N2/PPP2PPP/RNBQKB1R b KQkq d3 0 4 d5e4"
    "rnbqkbnr/pppp1ppp/8/4p3/1PB1P3/8/P1P2PPP/RNBQK1NR w KQkq - 0 3 b4f8"
    "r2qkbnr/pppb1ppp/2np4/4p3/4P3/2P2N2/PP1P1PPP/RNBQ1RK1 w kq - 1 7 d2d4"
    "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/8/PPP2PPP/RNBQK1NR w KQkq - 2 3 c1g5"
    "rnbqkb1r/pppp1ppp/5n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3 f6e4"
    "r2qkbnr/pppb1ppp/2np4/4p3/4P3/2P2N2/PP1P1PPP/RNBQ1RK1 b kq - 0 6 f8e7"
)

for full in "${test_cases[@]}"; do
    player_move="${full##* }"
    fen="${full% $player_move}"

    echo "FEN: $fen"
    echo "Player Move: $player_move"
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d '{"fen": "'"$fen"'", "move": "'"$player_move"'"}')

    score_diff=$(echo "$response" | jq -r '.score_difference')
    rating=$(echo "$response" | jq -r '.rating')

    echo "Score diff: $score_diff, Rating: $rating"
    echo "----------------------------"
done
