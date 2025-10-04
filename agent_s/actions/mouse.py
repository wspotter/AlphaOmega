"""
Mouse Action Handler
Controls mouse movement and clicks
"""
import logging
from typing import Dict, Any, Tuple

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
    # Fail-safe: move to corner to stop
    pyautogui.FAILSAFE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

logger = logging.getLogger("agent_s.actions.mouse")


class MouseAction:
    """Handle mouse control operations"""
    
    def __init__(self):
        if not PYAUTOGUI_AVAILABLE:
            logger.warning("pyautogui not available, mouse actions will fail")
        else:
            logger.info("MouseAction initialized with pyautogui")
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute mouse action
        
        Args:
            params: Dictionary with action parameters:
                - action: "click", "double_click", "right_click", "move", "drag"
                - x, y: Coordinates
                - button: "left", "right", "middle" (for clicks)
                - duration: Movement duration in seconds
                
        Returns:
            Result dictionary
        """
        if not PYAUTOGUI_AVAILABLE:
            raise RuntimeError("pyautogui not available for mouse control")
        
        action = params.get("action", "click")
        
        try:
            if action == "click":
                return self._click(params)
            elif action == "double_click":
                return self._double_click(params)
            elif action == "right_click":
                return self._right_click(params)
            elif action == "move":
                return self._move(params)
            elif action == "drag":
                return self._drag(params)
            elif action == "scroll":
                return self._scroll(params)
            else:
                raise ValueError(f"Unknown mouse action: {action}")
                
        except Exception as e:
            logger.error(f"Mouse action failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _click(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform mouse click"""
        x = params.get("x")
        y = params.get("y")
        button = params.get("button", "left")
        
        if x is not None and y is not None:
            pyautogui.click(x, y, button=button)
            logger.info(f"Clicked at ({x}, {y}) with {button} button")
        else:
            pyautogui.click(button=button)
            logger.info(f"Clicked at current position with {button} button")
        
        return {"success": True, "action": "click", "x": x, "y": y, "button": button}
    
    def _double_click(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform double click"""
        x = params.get("x")
        y = params.get("y")
        
        if x is not None and y is not None:
            pyautogui.doubleClick(x, y)
            logger.info(f"Double-clicked at ({x}, {y})")
        else:
            pyautogui.doubleClick()
            logger.info("Double-clicked at current position")
        
        return {"success": True, "action": "double_click", "x": x, "y": y}
    
    def _right_click(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform right click"""
        x = params.get("x")
        y = params.get("y")
        
        if x is not None and y is not None:
            pyautogui.rightClick(x, y)
            logger.info(f"Right-clicked at ({x}, {y})")
        else:
            pyautogui.rightClick()
            logger.info("Right-clicked at current position")
        
        return {"success": True, "action": "right_click", "x": x, "y": y}
    
    def _move(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Move mouse to position"""
        x = params.get("x")
        y = params.get("y")
        duration = params.get("duration", 0.5)
        
        if x is None or y is None:
            raise ValueError("x and y coordinates required for move action")
        
        pyautogui.moveTo(x, y, duration=duration)
        logger.info(f"Moved mouse to ({x}, {y})")
        
        return {"success": True, "action": "move", "x": x, "y": y}
    
    def _drag(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Drag mouse from current position or specified start to end"""
        x = params.get("x")
        y = params.get("y")
        duration = params.get("duration", 0.5)
        button = params.get("button", "left")
        
        if x is None or y is None:
            raise ValueError("x and y coordinates required for drag action")
        
        pyautogui.drag(x, y, duration=duration, button=button)
        logger.info(f"Dragged to ({x}, {y})")
        
        return {"success": True, "action": "drag", "x": x, "y": y}
    
    def _scroll(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Scroll mouse wheel"""
        clicks = params.get("clicks", 1)  # Positive = up, negative = down
        x = params.get("x")
        y = params.get("y")
        
        if x is not None and y is not None:
            pyautogui.moveTo(x, y)
        
        pyautogui.scroll(clicks)
        logger.info(f"Scrolled {clicks} clicks")
        
        return {"success": True, "action": "scroll", "clicks": clicks}
    
    def get_position(self) -> Tuple[int, int]:
        """Get current mouse position"""
        if not PYAUTOGUI_AVAILABLE:
            return (0, 0)
        
        return pyautogui.position()
