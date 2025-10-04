"""
Safety Validator for Agent-S Actions
Validates actions before execution to prevent dangerous operations
"""
import os
import re
import logging
from typing import Dict, Any, List
from pathlib import Path

logger = logging.getLogger("agent_s.safety")


class SafetyValidator:
    """Validate computer use actions for safety"""
    
    def __init__(self):
        # Load safety config from environment
        self.allow_file_write = os.getenv("AGENT_ALLOW_FILE_WRITE", "false").lower() == "true"
        self.allow_system_commands = os.getenv("AGENT_ALLOW_SYSTEM_COMMANDS", "false").lower() == "true"
        self.allow_app_launch = os.getenv("AGENT_ALLOW_APP_LAUNCH", "true").lower() == "true"
        
        # Allowed paths for file operations
        allowed_paths_str = os.getenv("AGENT_ALLOWED_PATHS", "/tmp,/home/*/Downloads")
        self.allowed_paths = [p.strip() for p in allowed_paths_str.split(",")]
        
        logger.info(f"SafetyValidator initialized:")
        logger.info(f"  - File write: {self.allow_file_write}")
        logger.info(f"  - System commands: {self.allow_system_commands}")
        logger.info(f"  - App launch: {self.allow_app_launch}")
        logger.info(f"  - Allowed paths: {self.allowed_paths}")
    
    def validate(self, action_plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a list of planned actions
        
        Args:
            action_plan: List of actions to validate
            
        Returns:
            Dictionary with:
                - safe: bool - whether actions are safe
                - reason: str - reason if not safe
                - warnings: list - non-blocking warnings
        """
        warnings = []
        
        for i, action in enumerate(action_plan):
            action_type = action.get("type")
            params = action.get("params", {})
            
            # Validate based on action type
            if action_type == "system_command":
                if not self.allow_system_commands:
                    return {
                        "safe": False,
                        "reason": "System commands are disabled by safety policy"
                    }
                
                # Check for dangerous commands
                cmd = params.get("command", "")
                if self._is_dangerous_command(cmd):
                    return {
                        "safe": False,
                        "reason": f"Dangerous system command blocked: {cmd}"
                    }
            
            elif action_type == "file_write":
                if not self.allow_file_write:
                    return {
                        "safe": False,
                        "reason": "File write operations are disabled by safety policy"
                    }
                
                # Check if path is allowed
                path = params.get("path", "")
                if not self._is_path_allowed(path):
                    return {
                        "safe": False,
                        "reason": f"File write to {path} is outside allowed directories"
                    }
            
            elif action_type == "app_launch":
                if not self.allow_app_launch:
                    return {
                        "safe": False,
                        "reason": "Application launch is disabled by safety policy"
                    }
            
            elif action_type == "keyboard":
                # Check for potentially dangerous key combinations
                if self._is_dangerous_keyboard(params):
                    warnings.append(f"Action {i+1}: Potentially risky keyboard action")
        
        return {
            "safe": True,
            "reason": None,
            "warnings": warnings
        }
    
    def _is_dangerous_command(self, command: str) -> bool:
        """Check if system command is dangerous"""
        dangerous_patterns = [
            r'\brm\s+-rf\s+/',  # rm -rf /
            r'\bdd\s+if=',      # dd if=
            r'\bmkfs\.',        # mkfs.*
            r'\bformat\b',      # format
            r'\b:(){:|:&};:',   # fork bomb
            r'\bshutdown\b',    # shutdown
            r'\breboot\b',      # reboot
            r'\bhalt\b',        # halt
            r'\bpoweroff\b',    # poweroff
            r'\bkillall\b',     # killall
            r'\bkill\s+-9\s+1', # kill -9 1 (init)
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                logger.warning(f"Dangerous command detected: {command}")
                return True
        
        return False
    
    def _is_path_allowed(self, path: str) -> bool:
        """Check if file path is in allowed directories"""
        path_obj = Path(path).resolve()
        
        for allowed_pattern in self.allowed_paths:
            # Handle wildcards in allowed paths
            allowed_pattern = allowed_pattern.replace("*", ".*")
            if re.match(allowed_pattern, str(path_obj)):
                return True
        
        return False
    
    def _is_dangerous_keyboard(self, params: Dict[str, Any]) -> bool:
        """Check if keyboard action is potentially dangerous"""
        # Check for hotkeys that might be dangerous
        dangerous_hotkeys = [
            ['ctrl', 'alt', 'delete'],  # Task manager / system interrupt
            ['alt', 'f4'],              # Close window
            ['ctrl', 'w'],              # Close tab
            ['ctrl', 'q'],              # Quit application
        ]
        
        if params.get("action") == "hotkey":
            keys = params.get("keys", [])
            if isinstance(keys, str):
                keys = keys.lower().split("+")
            else:
                keys = [k.lower() for k in keys]
            
            for dangerous in dangerous_hotkeys:
                if set(dangerous) == set(keys):
                    return True
        
        return False
    
    def validate_single_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single action"""
        return self.validate([action])
