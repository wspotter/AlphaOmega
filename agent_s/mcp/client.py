"""
MCP Client - Integration with mcpart server
Provides artifacts, memory, and file operations
"""
import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("agent_s.mcp")


class MCPClient:
    """Client for MCP server (mcpart) integration"""
    
    def __init__(self, server_url: str = "http://localhost:8002"):
        self.server_url = server_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"MCPClient initialized for {self.server_url}")
    
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict:
        """
        Execute an MCP tool
        
        Args:
            tool_name: Name of the tool to execute
            params: Tool parameters
            
        Returns:
            Tool execution result
        """
        try:
            logger.debug(f"Executing MCP tool: {tool_name}")
            
            response = await self.client.post(
                f"{self.server_url}/tools/{tool_name}",
                json=params
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.debug(f"MCP tool {tool_name} executed successfully")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"MCP tool execution failed: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Error executing MCP tool: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_artifact(
        self,
        content: str,
        artifact_type: str = "text",
        title: Optional[str] = None,
        language: Optional[str] = None
    ) -> Dict:
        """
        Create artifact using MCP server
        
        Args:
            content: Artifact content
            artifact_type: Type (text, code, markdown, etc.)
            title: Optional title
            language: Programming language for code artifacts
            
        Returns:
            Artifact creation result with URL
        """
        logger.info(f"Creating artifact: {title or 'untitled'}")
        
        params = {
            "content": content,
            "type": artifact_type
        }
        
        if title:
            params["title"] = title
        if language:
            params["language"] = language
        
        return await self.execute_tool("create_artifact", params)
    
    async def save_to_memory(self, key: str, value: Any) -> Dict:
        """
        Save data to persistent memory
        
        Args:
            key: Memory key
            value: Value to store (will be JSON serialized)
            
        Returns:
            Save result
        """
        logger.info(f"Saving to memory: {key}")
        
        return await self.execute_tool("save_memory", {
            "key": key,
            "value": value
        })
    
    async def read_from_memory(self, key: str) -> Dict:
        """
        Read data from persistent memory
        
        Args:
            key: Memory key to retrieve
            
        Returns:
            Retrieved value or error
        """
        logger.info(f"Reading from memory: {key}")
        
        return await self.execute_tool("read_memory", {
            "key": key
        })
    
    async def list_memory_keys(self) -> Dict:
        """List all memory keys"""
        return await self.execute_tool("list_memory_keys", {})
    
    async def read_file(self, path: str) -> Dict:
        """
        Read file content via MCP
        
        Args:
            path: File path to read
            
        Returns:
            File content
        """
        logger.info(f"Reading file: {path}")
        
        return await self.execute_tool("read_file", {
            "path": path
        })
    
    async def write_file(self, path: str, content: str) -> Dict:
        """
        Write file content via MCP
        
        Args:
            path: File path to write
            content: Content to write
            
        Returns:
            Write result
        """
        logger.info(f"Writing file: {path}")
        
        return await self.execute_tool("write_file", {
            "path": path,
            "content": content
        })
    
    async def list_files(self, directory: str = ".") -> Dict:
        """
        List files in directory
        
        Args:
            directory: Directory path
            
        Returns:
            List of files
        """
        return await self.execute_tool("list_files", {
            "directory": directory
        })
    
    async def is_connected(self) -> bool:
        """
        Check if MCP server is reachable
        
        Returns:
            True if connected, False otherwise
        """
        try:
            response = await self.client.get(f"{self.server_url}/health", timeout=5.0)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"MCP server not reachable: {e}")
            return False
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
