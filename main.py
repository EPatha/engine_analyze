"""Main application for real-time chess board analysis"""

import sys
import cv2
import numpy as np
import time
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import chess

from overlay import OverlayWindow
from screen_capture import ScreenCapture
from board_detector import ChessBoardDetector
from online_engine import OnlineEngine
import config


class AnalysisWorker(QThread):
    """Worker thread for chess engine analysis"""
    analysis_complete = pyqtSignal(dict)
    
    def __init__(self, engine, board):
        super().__init__()
        self.engine = engine
        self.board = board
        self._is_cancelled = False
        
    def run(self):
        """Run analysis in background thread"""
        try:
            if self._is_cancelled:
                return
                
            # Analyze position using online engine
            analysis = self.engine.analyze_position(self.board)
            
            if not self._is_cancelled:
                self.analysis_complete.emit(analysis)
        except Exception as e:
            if not self._is_cancelled:
                self.analysis_complete.emit({'error': str(e)})
    
    def cancel(self):
        """Cancel the analysis"""
        self._is_cancelled = True


class ChessAnalyzer(QWidget):
    """Main application window for chess analysis"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.overlay = OverlayWindow()
        self.screen_capture = ScreenCapture()
        self.board_detector = ChessBoardDetector()
        
        # Try to initialize engine, but continue if it fails
        try:
            self.chess_engine = ChessEngine()
            self.engine_available = self.chess_engine.engine is not None
        except Exception as e:
            print(f"Warning: Could not initialize engine: {e}")
            self.chess_engine = None
            self.engine_available = False
        
        # State
        self.current_board = chess.Board()
        self.analyzing = False
        self.last_analysis_time = 0
        self.analysis_worker = None
        self.last_fen = None
        self.analysis_enabled = False  # Analysis starts disabled
        self.engine_errors = 0  # Count engine errors
        Use online engine (Lichess Cloud Analysis)
        self.chess_engine = OnlineEngine()
        self.engine_available = True  # Online engine is always availabl config.CAPTURE_FPS)  # Convert FPS to milliseconds
        
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
        
        # Start/Stop button
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("▶ Start Analysis")
        self.start_button.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        
        # Disable button if engine not available
        if not self.engine_available:
            self.start_button.setEnabled(False)
            self.start_button.setText("⚠ Engine Not Available")
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #999999;
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    min-height: 30px;
                }
            """)
        else:
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px;
                    border-radius: 5px; (Online)")
        self.start_button.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
    # Best move display
        self.best_move_label = QLabel("Best Move: -")
        self.best_move_label.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        layout.addWidget(self.best_move_label)
         (Using Lichess Cloud)")
        self.status_label.setFont(QFont('Arial', 11))
        self.status_label.setStyleSheet("color: orange;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter
        self.top_moves_label.setWordWrap(True)
        layout.addWidget(self.top_moves_label)
        
        # Instructions
        instructions = QLabel(
            "\n📖 Instructions:\n"
            "• Drag overlay window over chess board\n"
            "• Resize overlay to match board size\n"
            "• Click 'Start Analysis' to begin\n"
            "• Press Q to quit"
        )
        instructions.setFont(QFont('Arial', 10))
        instructions.setStyleSheet("color: gray;")
        layout.addWidget(instructions)
        
        self.setLayout(layout)
    
    def toggle_analysis(self):
        """Toggle analysis on/off"""
        self.analysis_enabled = not self.analysis_enabled
        
        if self.analysis_enabled:
            self.start_button.setText("⏸ Stop Analysis")
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    min-height: 30px;
                }
                QPushButton:hover {
                    background-color: #da190b;
                }
            """)
            self.status_label.setText("Status: Running ▶")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.start_button.setText("▶ Start Analysis")
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    min-height: 30px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            self.status_label.setText("Status: Stopped ⏸")
            self.status_label.setStyleSheet("color: orange;")
        
    def update_analysis(self):
        """Update analysis based on current screen capture"""
        # Skip if analysis is not enabled
        if not self.analysis_enabled:
            return
             (Lichess Cloud)")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.start_button.setText("▶ Start Analysis (Online)")
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    min-height: 30px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            self.status_label.setText("Status: Stopped ⏸ (Lichess Cloud)
                self.fen_label.setText(f"Position: {fen[:50]}...")
                
                # Only analyze if:
                # 1. Not currently analyzing
                # 2. Engine is initialized
                # 3. Position has changed
                # 4. At least 2 seconds since last analysis
                # 5. Engine hasn't failed too many times
                current_time = time.time()
                if (not self.analyzing and 
                    self.engine_available and
                    self.chess_engine and
                    self.chess_engine.engine and 
                    fen != self.last_fen and
                    current_time - self.last_analysis_time > 2.0 and
                    self.engine_errors < 3):  # Stop after 3 errors
                    
                    self.analyzing = True
                    self.last_fen = fen
                    self.last_analysis_time = current_time
                    
                    # Run analysis in background thread with new engine instance
                    self.analysis_worker = AnalysisWorker(
                        self.chess_engine.stockfish_path, 
                        board
                    )
                    self.analysis_worker.analysis_complete.connect(self.on_analysis_complete)
                    self.analysis_worker.start()
                elif Position has changed
                # 3. At least 2 seconds since last analysis
                # 4. Engine hasn't failed too many times
                current_time = time.time()
                if (not self.analyzing and 
                    fen != self.last_fen and
                    current_time - self.last_analysis_time > 2.0 and
                    self.engine_errors < 5):  # Stop after 5 errors
                    
                    self.analyzing = True
                    self.last_fen = fen
                    self.last_analysis_time = current_time
                    
                    # Run analysis in background thread
                    self.analysis_worker = AnalysisWorker(
                        self.chess_engine, 
                        board
                    )
                    self.analysis_worker.analysis_complete.connect(self.on_analysis_complete)
                    self.analysis_worker.start()
                elif self.engine_errors >= 5:
                    # Too many errors, disable engine
                    self.status_label.setText("⚠ Too many errors - analysis disabled
                self.analysis_enabled = False
                self.start_button.setEnabled(False)
        else:
            # Reset error count on success
            self.engine_errors = 0
            
            # Update best move
            best_move = analysis.get('best_move_san', '-')
            best_move_uci = analysis.get('best_move_uci', '')
            
            self.best_move_label.setText(f"Best Move: {best_move}")
            self.best_move_label.setStyleSheet("color: green; font-size: 16px;")
            
            # Draw arrow on overlay
            if best_move_uci:
                self.overlay.set_best_move(best_move_uci)
            
            # Update evaluation
            evaluation = analysis.get('evaluation', '-')
            self.eval_label.setText(f"Evaluation: {evaluation}")
            5:
                self.status_label.setText("⚠ Analysis disabled (too many errors
            top_moves = analysis.get('top_moves', [])
            if top_moves:
                moves_text = "Top Moves:\n"
                for i, move_info in enumerate(top_moves, 1):
                    moves_text += f"{i}. {move_info['move_san']} ({move_info['evaluation']})\n"
                self.top_moves_label.setText(moves_text)
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Q:
            self.close()
            
    def closeEvent(self, event):
        """Clean up when closing"""
        self.capture_timer.stop()
        
        # Stop any running analysis
        if self.analysis_worker and self.analysis_worker.isRunning():
            self.analysis_worker.cancel()
            self.analysis_worker.terminate()
            self.analysis_worker.wait(1000)  # Wait max 1 second
        
        self.screen_capture.close()
        if self.chess_engine:
            try:
                self.chess_engine.close()
            except:
                pass
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
