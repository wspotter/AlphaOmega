"""
Keyboard Action Handler
Controls keyboard input
"""
import logging
from typing import Dict, Any, List
import time

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

logger = logging.getLogger("agent_s.actions.keyboard")


class KeyboardAction:
    """Handle keyboard input operations"""
    
    def __init__(self):
        if not PYAUTOGUI_AVAILABLE:
            logger.warning("pyautogui not available, keyboard actions will fail")
        else:
            logger.info("KeyboardAction initialized with pyautogui")
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute keyboard action
        
        Args:
            params: Dictionary with action parameters:
                - action: "type", "press", "hotkey", "write"
                - text: Text to type
                - key: Key to press
                - keys: List of keys for hotkey
                - interval: Time between keystrokes
                
        Returns:
            Result dictionary
        """
        if not PYAUTOGUI_AVAILABLE:
            raise RuntimeError("pyautogui not available for keyboard control")
        
        action = params.get("action", "type")
        
        try:
            if action == "type" or action == "write":
                return self._type_text(params)
            elif action == "press":
                return self._press_key(params)
            elif action == "hotkey":
                return self._hotkey(params)
            else:
                raise ValueError(f"Unknown keyboard action: {action}")
                
        except Exception as e:
            logger.error(f"Keyboard action failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _type_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Type text string"""
        text = params.get("text", "")
        interval = params.get("interval", 0.01)  # Delay between keystrokes
        
        if not text:
            raise ValueError("Text parameter required for type action")
        
        pyautogui.write(text, interval=interval)
        logger.info(f"Typed text: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        return {
            "success": True,
            "action": "type",
            "text_length": len(text)
        }
    
    def _press_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Press a single key or key combination"""
        key = params.get("key")
        presses = params.get("presses", 1)
        interval = params.get("interval", 0.1)
        
        if not key:
            raise ValueError("Key parameter required for press action")
        
        pyautogui.press(key, presses=presses, interval=interval)
        logger.info(f"Pressed key: {key} ({presses} times)")
        
        return {
            "success": True,
            "action": "press",
            "key": key,
            "presses": presses
        }
    
    def _hotkey(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Press multiple keys simultaneously (hotkey/shortcut)"""
        keys = params.get("keys", [])
        
        if not keys:
            raise ValueError("Keys parameter required for hotkey action")
        
        if isinstance(keys, str):
            keys = keys.split("+")
        
        pyautogui.hotkey(*keys)
        logger.info(f"Pressed hotkey: {'+'.join(keys)}")
        
        return {
            "success": True,
            "action": "hotkey",
            "keys": keys
        }
    
    def type_slowly(self, text: str, delay: float = 0.1):
        """Type text with visible delay (for demonstration)"""
        for char in text:
            pyautogui.write(char)
            time.sleep(delay)
    
    @staticmethod
    def get_special_keys() -> List[str]:
        """Return list of special key names that can be used"""
        return [
            'enter', 'return', 'tab', 'space', 'backspace', 'delete',
            'esc', 'escape', 'up', 'down', 'left', 'right',
            'home', 'end', 'pageup', 'pagedown',
            'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
            'shift', 'ctrl', 'control', 'alt', 'option', 'command', 'win', 'windows',
            'insert', 'printscreen', 'scrolllock', 'pause',
            'capslock', 'numlock'
        ]
