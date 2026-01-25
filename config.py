"""Configuration settings for chess analyzer"""

# Stockfish engine path - update this to your stockfish location
# macOS (Homebrew): /opt/homebrew/bin/stockfish or /usr/local/bin/stockfish
# Windows: C:/path/to/stockfish.exe
# Linux: /usr/games/stockfish or /usr/bin/stockfish
STOCKFISH_PATH = "/opt/homebrew/bin/stockfish"

# Engine settings
STOCKFISH_DEPTH = 15
STOCKFISH_TIME_LIMIT = 2.0  # seconds

# Detection settings
CAPTURE_FPS = 2  # Frames per second for real-time capture
MIN_CONTOUR_AREA = 1000

# Overlay window settings
DEFAULT_OVERLAY_SIZE = 600
OVERLAY_OPACITY = 0.3
RESIZE_HANDLE_SIZE = 20

# Colors (BGR format for OpenCV)
COLOR_OVERLAY = (0, 255, 0)  # Green
COLOR_GRID = (255, 0, 0)  # Blue
COLOR_HIGHLIGHT = (0, 255, 255)  # Yellow
