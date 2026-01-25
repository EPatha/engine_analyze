"""Real-time screen capture for chess board area"""

import mss
import numpy as np
from PIL import Image
import cv2


class ScreenCapture:
    """Capture screen area in real-time"""
    
    def __init__(self):
        self.sct = mss.mss()
        
    def capture_area(self, x, y, width, height):
        """
        Capture a specific area of the screen
        
        Args:
            x: X coordinate of top-left corner
            y: Y coordinate of top-left corner
            width: Width of capture area
            height: Height of capture area
            
        Returns:
            numpy array: Captured image in BGR format
        """
        # Define the monitor area to capture
        monitor = {
            "top": y,
            "left": x,
            "width": width,
            "height": height
        }
        
        # Capture the screen
        screenshot = self.sct.grab(monitor)
        
        # Convert to numpy array
        img = np.array(screenshot)
        
        # Convert BGRA to BGR (remove alpha channel)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        return img
    
    def capture_rect(self, rect):
        """
        Capture screen area from QRect object
        
        Args:
            rect: QRect object with capture coordinates
            
        Returns:
            numpy array: Captured image in BGR format
        """
        return self.capture_area(rect.x(), rect.y(), rect.width(), rect.height())
    
    def close(self):
        """Clean up resources"""
        self.sct.close()
