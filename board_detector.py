"""Chess board detection and piece recognition from digital chess boards"""

import cv2
import numpy as np
import chess


class ChessBoardDetector:
    """Detect chess board and pieces from screen capture"""
    
    def __init__(self):
        self.board_colors = {
            'light': [],
            'dark': []
        }
        
    def detect_board(self, image):
        """
        Detect chess board position and extract squares
        
        Args:
            image: BGR image from screen capture
            
        Returns:
            dict: Dictionary containing board state and detected position
        """
        height, width = image.shape[:2]
        
        # For digital chess boards, we can divide the image into 8x8 grid
        # since the overlay already matches the board size
        square_width = width // 8
        square_height = height // 8
        
        squares = []
        
        for row in range(8):
            row_squares = []
            for col in range(8):
                x = col * square_width
                y = row * square_height
                square = image[y:y+square_height, x:x+square_width]
                row_squares.append(square)
            squares.append(row_squares)
            
        return {
            'squares': squares,
            'square_width': square_width,
            'square_height': square_height
        }
    
    def get_square_color(self, square_img):
        """
        Get average color of a square to detect pieces
        
        Args:
            square_img: Image of a single chess square
            
        Returns:
            tuple: Average BGR color
        """
        # Get central region to avoid borders
        h, w = square_img.shape[:2]
        center_region = square_img[h//4:3*h//4, w//4:3*w//4]
        
        avg_color = cv2.mean(center_region)[:3]
        return avg_color
    
    def detect_piece_simple(self, square_img, is_light_square):
        """
        Simple piece detection based on color analysis
        
        Args:
            square_img: Image of a single chess square
            is_light_square: Boolean indicating if square is light or dark
            
        Returns:
            str: Piece type ('p', 'n', 'b', 'r', 'q', 'k', 'P', 'N', etc.) or None
        """
        # Get average color
        avg_color = self.get_square_color(square_img)
        
        # Convert to grayscale for brightness analysis
        gray = cv2.cvtColor(square_img, cv2.COLOR_BGR2GRAY)
        center_h, center_w = gray.shape[0]//4, gray.shape[1]//4
        center_region = gray[center_h:3*center_h, center_w:3*center_w]
        
        avg_brightness = np.mean(center_region)
        std_brightness = np.std(center_region)
        
        # High standard deviation suggests a piece (more contrast)
        # Low standard deviation suggests empty square
        if std_brightness < 15:
            return None  # Empty square
            
        # Determine if piece is white or black based on brightness
        # This is a simplified detection - you may need to adjust thresholds
        # based on the specific chess website's colors
        if avg_brightness > 127:
            # Likely a light/white piece
            return 'P'  # Default to pawn, needs more sophisticated detection
        else:
            # Likely a dark/black piece
            return 'p'  # Default to pawn
    
    def image_to_fen(self, image):
        """
        Convert chess board image to FEN notation
        
        Args:
            image: BGR image of chess board
            
        Returns:
            str: FEN string representing the position
        """
        board_data = self.detect_board(image)
        squares = board_data['squares']
        
        fen_rows = []
        
        for row_idx, row in enumerate(squares):
            fen_row = ""
            empty_count = 0
            
            for col_idx, square_img in enumerate(row):
                # Determine if square is light or dark
                is_light = (row_idx + col_idx) % 2 == 0
                
                piece = self.detect_piece_simple(square_img, is_light)
                
                if piece is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen_row += str(empty_count)
                        empty_count = 0
                    fen_row += piece
            
            if empty_count > 0:
                fen_row += str(empty_count)
                
            fen_rows.append(fen_row)
        
        # Join rows with '/'
        fen_position = '/'.join(fen_rows)
        
        # Add default game state (white to move, all castling available, etc.)
        # This is simplified - you may want to detect whose turn it is
        fen_full = f"{fen_position} w KQkq - 0 1"
        
        return fen_full
    
    def detect_pieces_advanced(self, image):
        """
        Advanced piece detection using template matching or ML
        This is a placeholder for more sophisticated detection
        
        Args:
            image: BGR image of chess board
            
        Returns:
            chess.Board: Python-chess board object
        """
        # For now, use simple detection
        fen = self.image_to_fen(image)
        
        try:
            board = chess.Board(fen)
            return board
        except:
            # If FEN is invalid, return starting position
            return chess.Board()
    
    def visualize_detection(self, image, board_data):
        """
        Draw detected squares on image for debugging
        
        Args:
            image: Original image
            board_data: Board detection data
            
        Returns:
            numpy array: Image with detection visualization
        """
        vis_img = image.copy()
        square_width = board_data['square_width']
        square_height = board_data['square_height']
        
        # Draw grid
        for i in range(9):
            # Vertical lines
            x = i * square_width
            cv2.line(vis_img, (x, 0), (x, image.shape[0]), (0, 255, 0), 2)
            
            # Horizontal lines
            y = i * square_height
            cv2.line(vis_img, (0, y), (image.shape[1], y), (0, 255, 0), 2)
        
        return vis_img
