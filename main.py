"""Main application for real-time chess board analysis"""

import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont
import chess

from overlay import OverlayWindow
from screen_capture import ScreenCapture
from board_detector import ChessBoardDetector
from chess_engine import ChessEngine
import config


class ChessAnalyzer(QWidget):
    """Main application window for chess analysis"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.overlay = OverlayWindow()
        self.screen_capture = ScreenCapture()
        self.board_detector = ChessBoardDetector()
        self.chess_engine = ChessEngine()
        
        # State
        self.current_board = chess.Board()
        self.analyzing = False
        
        # UI
        self.init_ui()
        
        # Timer for real-time capture
        self.capture_timer = QTimer()
        self.capture_timer.timeout.connect(self.update_analysis)
        self.capture_timer.start(1000 // config.CAPTURE_FPS)  # Convert FPS to milliseconds
        
        # Show overlay
        self.overlay.show()
        
    def init_ui(self):
        """Initialize the analysis display window"""
        self.setWindowTitle("Chess Analysis")
        self.setGeometry(100, 700, 400, 300)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("♟️ Real-time Chess Analyzer")
        title.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # FEN display
        self.fen_label = QLabel("Position: Waiting...")
        self.fen_label.setWordWrap(True)
        layout.addWidget(self.fen_label)
        
        # Best move display
        self.best_move_label = QLabel("Best Move: -")
        self.best_move_label.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        layout.addWidget(self.best_move_label)
        
        # Evaluation display
        self.eval_label = QLabel("Evaluation: -")
        self.eval_label.setFont(QFont('Arial', 12))
        layout.addWidget(self.eval_label)
        
        # Top moves display
        self.top_moves_label = QLabel("Top Moves:\n-")
        self.top_moves_label.setWordWrap(True)
        layout.addWidget(self.top_moves_label)
        
        # Instructions
        instructions = QLabel(
            "\n📖 Instructions:\n"
            "• Drag overlay window over chess board\n"
            "• Resize overlay to match board size\n"
            "• Analysis updates automatically\n"
            "• Press Q to quit"
        )
        instructions.setFont(QFont('Arial', 10))
        instructions.setStyleSheet("color: gray;")
        layout.addWidget(instructions)
        
        self.setLayout(layout)
        
    def update_analysis(self):
        """Update analysis based on current screen capture"""
        try:
            # Get capture rectangle from overlay
            capture_rect = self.overlay.get_capture_rect()
            
            # Capture screen
            screen_img = self.screen_capture.capture_rect(capture_rect)
            
            # Detect board and pieces
            fen = self.board_detector.image_to_fen(screen_img)
            
            try:
                # Create board from FEN
                board = chess.Board(fen)
                self.current_board = board
                
                # Update FEN display
                self.fen_label.setText(f"Position: {fen[:50]}...")
                
                # Analyze position
                if not self.analyzing and self.chess_engine.engine:
                    self.analyzing = True
                    analysis = self.chess_engine.analyze_position(board)
                    
                    if 'error' in analysis:
                        self.best_move_label.setText(f"Error: {analysis['error']}")
                    else:
                        # Update best move
                        best_move = analysis.get('best_move_san', '-')
                        self.best_move_label.setText(f"Best Move: {best_move}")
                        self.best_move_label.setStyleSheet("color: green; font-size: 16px;")
                        
                        # Update evaluation
                        evaluation = analysis.get('evaluation', '-')
                        self.eval_label.setText(f"Evaluation: {evaluation}")
                        
                        # Get top 3 moves
                        top_moves = self.chess_engine.get_top_moves(board, 3)
                        if top_moves:
                            moves_text = "Top Moves:\n"
                            for i, move_info in enumerate(top_moves, 1):
                                moves_text += f"{i}. {move_info['move_san']} ({move_info['evaluation']})\n"
                            self.top_moves_label.setText(moves_text)
                    
                    self.analyzing = False
                    
            except Exception as e:
                self.fen_label.setText(f"Detection error: {str(e)[:50]}")
                
        except Exception as e:
            print(f"Analysis error: {e}")
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Q:
            self.close()
            
    def closeEvent(self, event):
        """Clean up when closing"""
        self.capture_timer.stop()
        self.screen_capture.close()
        self.chess_engine.close()
        self.overlay.close()
        event.accept()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show analyzer
    analyzer = ChessAnalyzer()
    analyzer.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
