#!/usr/bin/env python3
"""
Simple Chess Board FEN Reader
Only reads FEN from screen - no engine analysis
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont

from overlay import OverlayWindow
from screen_capture import ScreenCapture
from board_detector import ChessBoardDetector

class SimpleFENReader(QWidget):
    def __init__(self):
        super().__init__()
        
        # Components
        self.overlay = OverlayWindow()
        self.screen_capture = ScreenCapture()
        self.board_detector = ChessBoardDetector()
        
        # State
        self.reading_enabled = False
        self.current_fen = ""
        
        # Timer for updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_fen)
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Simple Chess FEN Reader')
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Chess Board FEN Reader")
        title.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel(
            "\nInstructions:\n"
            "1. Position overlay over chess board\n"
            "2. Resize overlay to match board\n"
            "3. Click Start to read FEN\n"
            "4. FEN will update automatically"
        )
        instructions.setFont(QFont('Arial', 11))
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instructions)
        
        # Start/Stop button
        self.start_button = QPushButton("Start FEN Reading")
        self.start_button.clicked.connect(self.toggle_reading)
        self.start_button.setFont(QFont('Arial', 12))
        self.start_button.setFixedHeight(40)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(self.start_button)
        
        # Status
        self.status_label = QLabel("Status: Stopped")
        self.status_label.setFont(QFont('Arial', 10))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: orange; padding: 10px;")
        layout.addWidget(self.status_label)
        
        # FEN display
        self.fen_label = QLabel("FEN: Not reading")
        self.fen_label.setFont(QFont('Courier', 10))
        self.fen_label.setWordWrap(True)
        self.fen_label.setStyleSheet("""
            background-color: #f0f0f0;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
        """)
        layout.addWidget(self.fen_label)
        
        # Quit button
        quit_button = QPushButton("Quit")
        quit_button.clicked.connect(self.close)
        quit_button.setFont(QFont('Arial', 10))
        quit_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        layout.addWidget(quit_button)
        
        self.setLayout(layout)
        
    def toggle_reading(self):
        if self.reading_enabled:
            # Stop reading
            self.reading_enabled = False
            self.timer.stop()
            self.start_button.setText("Start FEN Reading")
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 5px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            self.status_label.setText("Status: Stopped")
            self.status_label.setStyleSheet("color: orange;")
        else:
            # Start reading
            self.reading_enabled = True
            self.timer.start(2000)  # Update every 2 seconds
            self.start_button.setText("Stop FEN Reading")
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border-radius: 5px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #da190b;
                }
            """)
            self.status_label.setText("Status: Reading FEN...")
            self.status_label.setStyleSheet("color: green;")
            
    def update_fen(self):
        if not self.reading_enabled:
            return
            
        try:
            # Get overlay position
            x, y, width, height = self.overlay.get_position()
            
            # Capture screen
            image = self.screen_capture.capture_rect(x, y, width, height)
            
            if image is not None:
                # Convert to FEN
                fen = self.board_detector.image_to_fen(image)
                
                if fen and fen != self.current_fen:
                    self.current_fen = fen
                    self.fen_label.setText(f"FEN: {fen}")
                    self.status_label.setText("Status: FEN Updated ✓")
                    print(f"New FEN: {fen}")
                else:
                    self.status_label.setText("Status: Reading FEN...")
            else:
                self.status_label.setText("Status: No image captured")
                
        except Exception as e:
            print(f"Error updating FEN: {e}")
            self.status_label.setText(f"Status: Error - {e}")
            self.status_label.setStyleSheet("color: red;")
            
    def closeEvent(self, event):
        if hasattr(self, 'timer'):
            self.timer.stop()
        if hasattr(self, 'overlay'):
            self.overlay.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Show overlay first
    overlay = OverlayWindow()
    overlay.show()
    
    # Show main window
    reader = SimpleFENReader()
    reader.overlay = overlay  # Use same overlay
    reader.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()