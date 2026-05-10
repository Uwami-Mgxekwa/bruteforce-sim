#!/bin/bash
echo "========================================"
echo "  Brute Force Simulator Launcher"
echo "========================================"
echo "Select mode to run:"
echo "1. Server Mode"
echo "2. Attack Mode"
echo ""
read -p "Enter 1 or 2: " mode

if [ "$mode" = "1" ]; then
    echo "Starting Server..."
    python3 bruteforce.py --mode server
elif [ "$mode" = "2" ]; then
    echo "Starting Attacker..."
    python3 bruteforce.py --mode attack
else
    echo "Invalid choice. Showing help instead..."
    python3 bruteforce.py --help
fi

echo ""
read -p "Press Enter to exit..."
