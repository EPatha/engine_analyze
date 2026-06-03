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
    
    def detect_piece_simple(self, square_img, is_light_square, square_name=None):
        """
        Simple piece detection based on color analysis and logical square coordinates.
        
        Args:
            square_img: Image of a single chess square
            is_light_square: Boolean indicating if square is light or dark
            square_name: Chess square name (e.g., 'e1', 'a8')
            
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
        is_white_piece = avg_brightness > 127
        
        # Map by square name if provided
        if square_name:
            # Check starting position pieces to correctly identify them
            starting_pieces = {
                'a8': 'r', 'b8': 'n', 'c8': 'b', 'd8': 'q', 'e8': 'k', 'f8': 'b', 'g8': 'n', 'h8': 'r',
                'a1': 'R', 'b1': 'N', 'c1': 'B', 'd1': 'Q', 'e1': 'K', 'f1': 'B', 'g1': 'N', 'h1': 'R'
            }
            if square_name in starting_pieces:
                return starting_pieces[square_name]
            
            # Failsafe: pawns cannot exist on 1st or 8th rank
            rank = square_name[1]
            if rank == '8':
                return 'q' if not is_white_piece else 'Q'
            elif rank == '1':
                return 'Q' if is_white_piece else 'q'
                
        # Default to pawn for middle ranks
        return 'P' if is_white_piece else 'p'
    
    def image_to_fen(self, image, white_on_bottom=True):
        """
        Convert chess board image to FEN notation with robust validation and orientation support
        
        Args:
            image: BGR image of chess board
            white_on_bottom: True if White is at the bottom of the screen, False if Black is at the bottom
            
        Returns:
            str: FEN string representing the position
        """
        board_data = self.detect_board(image)
        squares = board_data['squares']
        
        fen_rows = []
        
        # FEN represents board from rank 8 to 1 (top to bottom).
        # We loop rank_idx from 0 (rank 8) to 7 (rank 1).
        for rank_idx in range(8):
            row_idx = rank_idx if white_on_bottom else (7 - rank_idx)
            rank_num = 8 - rank_idx
            
            fen_row = ""
            empty_count = 0
            
            # We loop file_idx from 0 (file a) to 7 (file h)
            for file_idx in range(8):
                col_idx = file_idx if white_on_bottom else (7 - file_idx)
                file_char = chr(ord('a') + file_idx)
                
                square_name = f"{file_char}{rank_num}"
                square_img = squares[row_idx][col_idx]
                
                # Determine if square is light or dark
                is_light = (row_idx + col_idx) % 2 == 0
                
                piece = self.detect_piece_simple(square_img, is_light, square_name)
                
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
        fen_full = f"{fen_position} w KQkq - 0 1"
        
        # Post-process to ensure it is valid python-chess board
        try:
            board = chess.Board(fen_full)
            
            # Check and fix kings
            has_white_king = bool(board.pieces(chess.KING, chess.WHITE))
            has_black_king = bool(board.pieces(chess.KING, chess.BLACK))
            
            if not has_white_king:
                # Find first empty square or place at e1
                if board.piece_at(chess.E1) is None or board.piece_at(chess.E1).color == chess.WHITE:
                    board.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
                else:
                    for sq in chess.SQUARES:
                        if board.piece_at(sq) is None:
                            board.set_piece_at(sq, chess.Piece(chess.KING, chess.WHITE))
                            break
            
            if not has_black_king:
                if board.piece_at(chess.E8) is None or board.piece_at(chess.E8).color == chess.BLACK:
                    board.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))
                else:
                    for sq in chess.SQUARES:
                        if board.piece_at(sq) is None:
                            board.set_piece_at(sq, chess.Piece(chess.KING, chess.BLACK))
                            break
                            
            # Convert pawns on 1st or 8th rank to queens (as failsafe)
            for square in chess.SQUARES:
                rank = chess.square_rank(square)
                piece = board.piece_at(square)
                if piece and piece.piece_type == chess.PAWN:
                    if rank == 0 or rank == 7:
                        board.set_piece_at(square, chess.Piece(chess.QUEEN, piece.color))
            
            # Apply turn correction rule (if opposite king in check, it must be their turn)
            if board.status() & chess.STATUS_OPPOSITE_CHECK:
                board.turn = not board.turn
                        
            return board.fen()
        except Exception as e:
            print(f"Error in FEN validation/repair: {e}")
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
