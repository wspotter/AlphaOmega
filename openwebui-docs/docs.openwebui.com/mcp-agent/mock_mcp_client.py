"""
Mock MCP Client
Simulates the behavior of a Model Context Protocol (MCP) client
for demonstration purposes. This represents the stateful MCP server
that would typically run via stdio.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class MockCUAClient:
    """
    Mock Computer Use Agent (CUA) MCP Client
    
    This class simulates a stateful MCP server that maintains context
    and state across multiple interactions. In a real implementation,
    this would communicate with an actual MCP server via stdio.
    """
    
    def __init__(self):
        """Initialize the mock MCP client with a simulated file system"""
        self.connected = False
        self.session_id: Optional[str] = None
        
        # Simulated file system state
        self.filesystem: Dict[str, Any] = {
            "/home/user/Desktop": {
                "type": "directory",
                "contents": {
                    "document.txt": {
                        "type": "file",
                        "content": "This is a sample document.",
                        "size": "26 bytes",
                        "modified": "2025-10-14 10:30:00"
                    },
                    "presentation.pptx": {
                        "type": "file",
                        "content": "[PowerPoint file]",
                        "size": "2.4 MB",
                        "modified": "2025-10-13 15:45:00"
                    },
                    "notes.md": {
                        "type": "file",
                        "content": "# Meeting Notes\n- Discuss Q4 goals\n- Review project timeline",
                        "size": "58 bytes",
                        "modified": "2025-10-14 09:15:00"
                    }
                }
            },
            "/home/user/Documents": {
                "type": "directory",
                "contents": {
                    "report.pdf": {
                        "type": "file",
                        "content": "[PDF file]",
                        "size": "1.2 MB",
                        "modified": "2025-10-12 14:20:00"
                    }
                }
            }
        }
        
        # Command history for state tracking
        self.command_history: List[Dict[str, Any]] = []
        
        # Current working directory
        self.current_directory = "/home/user/Desktop"
    
    def connect(self) -> Dict[str, Any]:
        """
        Establish connection to the mock MCP server
        
        Returns:
            Connection status and session information
        """
        self.connected = True
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "status": "connected",
            "session_id": self.session_id,
            "message": "Successfully connected to Mock CUA MCP Server",
            "capabilities": [
                "file_operations",
                "directory_listing",
                "text_reading",
                "state_management"
            ]
        }
    
    def disconnect(self) -> Dict[str, Any]:
        """
        Disconnect from the mock MCP server
        
        Returns:
            Disconnection status
        """
        self.connected = False
        session_id = self.session_id
        self.session_id = None
        
        return {
            "status": "disconnected",
            "session_id": session_id,
            "message": "Successfully disconnected from Mock CUA MCP Server"
        }
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """
        Execute a command on the mock MCP server
        
        Args:
            command: The command string to execute
            
        Returns:
            Command execution result with observation
        """
        if not self.connected:
            return {
                "status": "error",
                "error": "Not connected to MCP server. Call connect() first.",
                "command": command
            }
        
        # Record command in history
        command_record = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "session_id": self.session_id
        }
        self.command_history.append(command_record)
        
        # Parse and execute command
        command_lower = command.lower().strip()
        
        if command_lower.startswith("list files") or command_lower.startswith("ls"):
            return self._list_files(command)
        elif command_lower.startswith("read file") or command_lower.startswith("cat"):
            return self._read_file(command)
        elif command_lower.startswith("change directory") or command_lower.startswith("cd"):
            return self._change_directory(command)
        elif command_lower.startswith("get current directory") or command_lower.startswith("pwd"):
            return self._get_current_directory()
        elif command_lower.startswith("create file"):
            return self._create_file(command)
        elif command_lower.startswith("help"):
            return self._get_help()
        else:
            return {
                "status": "error",
                "error": f"Unknown command: '{command}'. Type 'help' for available commands.",
                "command": command
            }
    
    def _list_files(self, command: str) -> Dict[str, Any]:
        """List files in the current or specified directory"""
        # Extract directory from command if provided
        parts = command.split()
        if len(parts) > 2:
            directory = " ".join(parts[2:])
        else:
            directory = self.current_directory
        
        if directory not in self.filesystem:
            return {
                "status": "error",
                "error": f"Directory not found: {directory}",
                "command": command
            }
        
        dir_data = self.filesystem[directory]
        if dir_data["type"] != "directory":
            return {
                "status": "error",
                "error": f"Not a directory: {directory}",
                "command": command
            }
        
        files = []
        for name, data in dir_data["contents"].items():
            files.append({
                "name": name,
                "type": data["type"],
                "size": data.get("size", "N/A"),
                "modified": data.get("modified", "N/A")
            })
        
        return {
            "status": "success",
            "command": command,
            "directory": directory,
            "files": files,
            "observation": f"Found {len(files)} items in {directory}"
        }
    
    def _read_file(self, command: str) -> Dict[str, Any]:
        """Read the contents of a file"""
        parts = command.split(maxsplit=2)
        if len(parts) < 3:
            return {
                "status": "error",
                "error": "Usage: read file <filename>",
                "command": command
            }
        
        filename = parts[2]
        
        # Search for file in current directory
        if self.current_directory in self.filesystem:
            dir_contents = self.filesystem[self.current_directory]["contents"]
            if filename in dir_contents:
                file_data = dir_contents[filename]
                if file_data["type"] == "file":
                    return {
                        "status": "success",
                        "command": command,
                        "filename": filename,
                        "content": file_data["content"],
                        "size": file_data["size"],
                        "observation": f"Successfully read file: {filename}"
                    }
        
        return {
            "status": "error",
            "error": f"File not found: {filename}",
            "command": command
        }
    
    def _change_directory(self, command: str) -> Dict[str, Any]:
        """Change the current working directory"""
        parts = command.split(maxsplit=2)
        if len(parts) < 3:
            return {
                "status": "error",
                "error": "Usage: change directory <path>",
                "command": command
            }
        
        directory = parts[2]
        
        if directory not in self.filesystem:
            return {
                "status": "error",
                "error": f"Directory not found: {directory}",
                "command": command
            }
        
        self.current_directory = directory
        return {
            "status": "success",
            "command": command,
            "directory": directory,
            "observation": f"Changed directory to: {directory}"
        }
    
    def _get_current_directory(self) -> Dict[str, Any]:
        """Get the current working directory"""
        return {
            "status": "success",
            "command": "get current directory",
            "directory": self.current_directory,
            "observation": f"Current directory: {self.current_directory}"
        }
    
    def _create_file(self, command: str) -> Dict[str, Any]:
        """Create a new file (simulated)"""
        parts = command.split(maxsplit=2)
        if len(parts) < 3:
            return {
                "status": "error",
                "error": "Usage: create file <filename>",
                "command": command
            }
        
        filename = parts[2]
        
        if self.current_directory in self.filesystem:
            dir_contents = self.filesystem[self.current_directory]["contents"]
            if filename in dir_contents:
                return {
                    "status": "error",
                    "error": f"File already exists: {filename}",
                    "command": command
                }
            
            # Create new file
            dir_contents[filename] = {
                "type": "file",
                "content": "",
                "size": "0 bytes",
                "modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return {
                "status": "success",
                "command": command,
                "filename": filename,
                "observation": f"Created new file: {filename}"
            }
        
        return {
            "status": "error",
            "error": "Current directory not accessible",
            "command": command
        }
    
    def _get_help(self) -> Dict[str, Any]:
        """Get list of available commands"""
        commands = [
            "list files [directory] - List files in directory",
            "read file <filename> - Read file contents",
            "change directory <path> - Change current directory",
            "get current directory - Show current directory",
            "create file <filename> - Create a new file",
            "help - Show this help message"
        ]
        
        return {
            "status": "success",
            "command": "help",
            "available_commands": commands,
            "observation": "Available commands listed"
        }
    
    def get_observation(self) -> Dict[str, Any]:
        """
        Get current state observation from the MCP server
        
        Returns:
            Current state information
        """
        if not self.connected:
            return {
                "status": "disconnected",
                "message": "No active connection"
            }
        
        return {
            "status": "connected",
            "session_id": self.session_id,
            "current_directory": self.current_directory,
            "command_count": len(self.command_history),
            "last_command": self.command_history[-1] if self.command_history else None
        }
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get complete state information
        
        Returns:
            Complete state snapshot
        """
        return {
            "connected": self.connected,
            "session_id": self.session_id,
            "current_directory": self.current_directory,
            "filesystem": self.filesystem,
            "command_history": self.command_history
        }

