# Chess Board Real-time Analyzer

Educational tool for analyzing chess positions in real-time using Stockfish engine via scanning live chess boards.

## Features
- Movable square overlay for board detection
- Real-time screen capture
- Chess board and piece detection
- Stockfish engine integration
- Best move suggestions
- Chess advantage analysis

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Stockfish:
   - macOS: `brew install stockfish`
   - Or download from: https://stockfishchess.org/download/

3. Update `config.py` with your Stockfish path

## Usage

```bash
python main.py
```

- Drag the overlay window to position over the chess board
- Resize using corner handles
- Press 'Space' to analyze current position
- Press 'Q' to quit

## Educational Purpose Only
This tool is designed for learning and analysis purposes only.
