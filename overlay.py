"""Movable and resizable overlay window for selecting chess board area"""

import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QRect, QPoint, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath
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
        self.best_move_arrow = None  # Store best move for drawing arrow
        self.white_on_bottom = True
        
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
        
        # Draw best move arrow if available
        if self.best_move_arrow:
            self.draw_arrow(painter, self.best_move_arrow)
        
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
    
    
    def set_best_move(self, move_uci):
        """
        Set the best move to display as an arrow
        
        Args:
            move_uci: Move in UCI format (e.g., 'e2e4', 'e7e5')
        """
        self.best_move_arrow = move_uci
        self.update()  # Trigger repaint
    
    def clear_best_move(self):
        """Clear the best move arrow"""
        self.best_move_arrow = None
        self.update()
    
    def uci_to_coords(self, square):
        """
        Convert chess square notation to pixel coordinates
        
        Args:
            square: Square notation (e.g., 'e2', 'e4')
            
        Returns:
            tuple: (x, y) pixel coordinates at center of square
        """
        if self.white_on_bottom:
            file = ord(square[0]) - ord('a')  # 0-7
            rank = 8 - int(square[1])  # 0-7 (reversed for display)
        else:
            file = 7 - (ord(square[0]) - ord('a'))  # 0-7
            rank = int(square[1]) - 1  # 0-7 (reversed for display)
        
        cell_width = self.width() / 8
        cell_height = self.height() / 8
        
        x = (file + 0.5) * cell_width
        y = (rank + 0.5) * cell_height
        
        return (x, y)
    
    def draw_arrow(self, painter, move_uci):
        """
        Draw an arrow showing the best move
        
        Args:
            painter: QPainter object
            move_uci: Move in UCI format (e.g., 'e2e4')
        """
        if not move_uci or len(move_uci) < 4:
            return
        
        from_square = move_uci[:2]
        to_square = move_uci[2:4]
        
        from_x, from_y = self.uci_to_coords(from_square)
        to_x, to_y = self.uci_to_coords(to_square)
        
        # Set arrow style
        arrow_color = QColor(255, 200, 0, 200)  # Yellow with transparency
        painter.setPen(QPen(arrow_color, 8, Qt.PenStyle.SolidLine))
        painter.setBrush(arrow_color)
        
        # Draw arrow line
        from_point = QPointF(from_x, from_y)
        to_point = QPointF(to_x, to_y)
        
        painter.drawLine(from_point, to_point)
        
        # Draw arrowhead
        arrow_size = 20
        
        # Calculate angle
        import math
        angle = math.atan2(to_y - from_y, to_x - from_x)
        
        # Arrowhead points
        arrow_p1 = QPointF(
            to_x - arrow_size * math.cos(angle - math.pi / 6),
            to_y - arrow_size * math.sin(angle - math.pi / 6)
        )
        arrow_p2 = QPointF(
            to_x - arrow_size * math.cos(angle + math.pi / 6),
            to_y - arrow_size * math.sin(angle + math.pi / 6)
        )
        
        # Draw filled arrowhead
        path = QPainterPath()
        path.moveTo(to_point)
        path.lineTo(arrow_p1)
        path.lineTo(arrow_p2)
        path.closeSubpath()
        
        painter.fillPath(path, arrow_color)
    def get_capture_rect(self):
        """Get the rectangle coordinates for screen capture"""
        geometry = self.geometry()
        return QRect(geometry.x(), geometry.y(), geometry.width(), geometry.height())
