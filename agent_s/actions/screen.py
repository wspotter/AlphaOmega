"""
Screen Capture Action Handler
Captures screenshots for vision analysis
"""
import os
import time
from datetime import datetime
from pathlib import Path
import logging

try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

logger = logging.getLogger("agent_s.actions.screen")


class ScreenAction:
    """Handle screen capture operations"""
    
    def __init__(self):
        self.screenshot_dir = os.getenv("SCREENSHOT_DIR", "/tmp/agent_screenshots")
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # Determine best capture method
        if MSS_AVAILABLE:
            self.capture_method = "mss"
            self.sct = mss.mss()
        elif PYAUTOGUI_AVAILABLE:
            self.capture_method = "pyautogui"
        else:
            self.capture_method = "scrot"
        
        logger.info(f"ScreenAction initialized with method: {self.capture_method}")
    
    def capture(self, region: tuple = None) -> str:
        """
        Capture screenshot
        
        Args:
            region: Optional (x, y, width, height) to capture specific region
            
        Returns:
            Path to saved screenshot
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"screen_{timestamp}.png"
        filepath = os.path.join(self.screenshot_dir, filename)
        
        try:
            if self.capture_method == "mss":
                return self._capture_mss(filepath, region)
            elif self.capture_method == "pyautogui":
                return self._capture_pyautogui(filepath, region)
            else:
                return self._capture_scrot(filepath, region)
        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}")
            raise
    
    def _capture_mss(self, filepath: str, region: tuple = None) -> str:
        """Capture using mss (fastest method)"""
        if region:
            x, y, w, h = region
            monitor = {"top": y, "left": x, "width": w, "height": h}
        else:
            monitor = self.sct.monitors[1]  # Primary monitor
        
        screenshot = self.sct.grab(monitor)
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=filepath)
        
        logger.debug(f"Screenshot captured with mss: {filepath}")
        return filepath
    
    def _capture_pyautogui(self, filepath: str, region: tuple = None) -> str:
        """Capture using pyautogui"""
        if region:
            screenshot = pyautogui.screenshot(region=region)
        else:
            screenshot = pyautogui.screenshot()
        
        screenshot.save(filepath)
        logger.debug(f"Screenshot captured with pyautogui: {filepath}")
        return filepath
    
    def _capture_scrot(self, filepath: str, region: tuple = None) -> str:
        """Capture using scrot command line tool"""
        import subprocess
        
        if region:
            x, y, w, h = region
            cmd = ["scrot", "-a", f"{x},{y},{w},{h}", filepath]
        else:
            cmd = ["scrot", filepath]
        
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"scrot failed: {result.stderr.decode()}")
        
        logger.debug(f"Screenshot captured with scrot: {filepath}")
        return filepath
    
    def capture_window(self, window_title: str = None) -> str:
        """Capture specific window (if supported)"""
        # TODO: Implement window-specific capture
        logger.warning("Window-specific capture not yet implemented, using full screen")
        return self.capture()
    
    def get_screen_size(self) -> tuple:
        """Get screen dimensions"""
        if self.capture_method == "mss":
            monitor = self.sct.monitors[1]
            return (monitor["width"], monitor["height"])
        elif PYAUTOGUI_AVAILABLE:
            return pyautogui.size()
        else:
            # Default guess
            return (1920, 1080)
