"""Movable and resizable overlay window for selecting chess board area"""

import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen
import config


class OverlayWindow(QWidget):
    """Transparent overlay window that can be moved and resized"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.dragging = False
        self.resizing = False
        self.drag_position = QPoint()
        self.resize_corner = None
        
    def init_ui(self):
        """Initialize the overlay window"""
        # Window settings
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set initial size and position
        size = config.DEFAULT_OVERLAY_SIZE
        self.setGeometry(100, 100, size, size)
        
        # Set window title (for debugging)
        self.setWindowTitle("Chess Board Selector")
        
    def paintEvent(self, event):
        """Draw the overlay rectangle and grid"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw semi-transparent background
        bg_color = QColor(*config.COLOR_OVERLAY)
        bg_color.setAlphaF(config.OVERLAY_OPACITY)
        painter.fillRect(self.rect(), bg_color)
        
        # Draw border
        pen = QPen(QColor(*config.COLOR_OVERLAY), 3)
        painter.setPen(pen)
        painter.drawRect(2, 2, self.width() - 4, self.height() - 4)
        
        # Draw 8x8 grid for chess board
        pen = QPen(QColor(*config.COLOR_GRID), 1)
        painter.setPen(pen)
        
        cell_width = self.width() / 8
        cell_height = self.height() / 8
        
        for i in range(1, 8):
            # Vertical lines
            x = int(i * cell_width)
            painter.drawLine(x, 0, x, self.height())
            
            # Horizontal lines
            y = int(i * cell_height)
            painter.drawLine(0, y, self.width(), y)
        
        # Draw resize handles at corners
        handle_size = config.RESIZE_HANDLE_SIZE
        handle_color = QColor(*config.COLOR_HIGHLIGHT)
        painter.setBrush(handle_color)
        
        # Top-left
        painter.drawRect(0, 0, handle_size, handle_size)
        # Top-right
        painter.drawRect(self.width() - handle_size, 0, handle_size, handle_size)
        # Bottom-left
        painter.drawRect(0, self.height() - handle_size, handle_size, handle_size)
        # Bottom-right
        painter.drawRect(self.width() - handle_size, self.height() - handle_size, 
                        handle_size, handle_size)
        
    def mousePressEvent(self, event):
        """Handle mouse press for dragging or resizing"""
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.pos()
            handle_size = config.RESIZE_HANDLE_SIZE
            
            # Check if clicking on a resize handle
            if self.is_in_corner(pos, 'top-left'):
                self.resizing = True
                self.resize_corner = 'top-left'
            elif self.is_in_corner(pos, 'top-right'):
                self.resizing = True
                self.resize_corner = 'top-right'
            elif self.is_in_corner(pos, 'bottom-left'):
                self.resizing = True
                self.resize_corner = 'bottom-left'
            elif self.is_in_corner(pos, 'bottom-right'):
                self.resizing = True
                self.resize_corner = 'bottom-right'
            else:
                # Start dragging
                self.dragging = True
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging or resizing"""
        if self.dragging:
            # Move window
            self.move(event.globalPosition().toPoint() - self.drag_position)
            
        elif self.resizing:
            # Resize window
            global_pos = event.globalPosition().toPoint()
            rect = self.geometry()
            
            if self.resize_corner == 'bottom-right':
                new_width = max(200, global_pos.x() - rect.x())
                new_height = max(200, global_pos.y() - rect.y())
                # Keep it square
                new_size = max(new_width, new_height)
                self.resize(new_size, new_size)
                
            elif self.resize_corner == 'top-left':
                new_x = global_pos.x()
                new_y = global_pos.y()
                new_width = max(200, rect.right() - new_x)
                new_height = max(200, rect.bottom() - new_y)
                new_size = max(new_width, new_height)
                self.setGeometry(rect.right() - new_size, rect.bottom() - new_size, 
                               new_size, new_size)
                
            elif self.resize_corner == 'top-right':
                new_width = max(200, global_pos.x() - rect.x())
                new_y = global_pos.y()
                new_height = max(200, rect.bottom() - new_y)
                new_size = max(new_width, new_height)
                self.setGeometry(rect.x(), rect.bottom() - new_size, new_size, new_size)
                
            elif self.resize_corner == 'bottom-left':
                new_x = global_pos.x()
                new_width = max(200, rect.right() - new_x)
                new_height = max(200, global_pos.y() - rect.y())
                new_size = max(new_width, new_height)
                self.setGeometry(rect.right() - new_size, rect.y(), new_size, new_size)
                
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.resizing = False
            self.resize_corner = None
            
    def is_in_corner(self, pos, corner):
        """Check if position is in a resize handle corner"""
        handle_size = config.RESIZE_HANDLE_SIZE
        
        if corner == 'top-left':
            return pos.x() < handle_size and pos.y() < handle_size
        elif corner == 'top-right':
            return pos.x() > self.width() - handle_size and pos.y() < handle_size
        elif corner == 'bottom-left':
            return pos.x() < handle_size and pos.y() > self.height() - handle_size
        elif corner == 'bottom-right':
            return (pos.x() > self.width() - handle_size and 
                   pos.y() > self.height() - handle_size)
        return False
    
    def get_capture_rect(self):
        """Get the rectangle coordinates for screen capture"""
        geometry = self.geometry()
        return QRect(geometry.x(), geometry.y(), geometry.width(), geometry.height())
