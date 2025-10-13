"""
AlphaOmega Pipeline Router for OpenWebUI
Routes requests intelligently to: Ollama (vision/reasoning/code), ComfyUI, Agent-S, MCP
"""
from typing import Optional, List, Dict, Any, AsyncGenerator
import json
import re
import os
from pydantic import BaseModel, Field
import httpx
import asyncio
from datetime import datetime


class Pipeline:
    """Intelligent router for AlphaOmega multi-backend system"""
    
    class Valves(BaseModel):
        """Pipeline configuration - editable from OpenWebUI"""
        OLLAMA_VISION_HOST: str = Field(
            default="http://localhost:11434",
            description="Ollama endpoint (GPU1 MI50 - LLaVA, Mistral, CodeLlama)"
        )
        OLLAMA_REASONING_HOST: str = Field(
            default="http://localhost:11434",
            description="Ollama endpoint (same as vision - single instance)"
        )
        COMFYUI_HOST: str = Field(
            default="http://localhost:8188",
            description="ComfyUI endpoint (GPU2 MI50 - Image generation)"
        )
        AGENT_S_HOST: str = Field(
            default="http://localhost:8001",
            description="Agent-S endpoint (Computer use)"
        )
        MCP_HOST: str = Field(
            default="http://localhost:8002",
            description="MCP server endpoint (Artifacts, memory, files)"
        )
        VISION_MODEL: str = Field(
            default="devstral-vision",
            description="Vision model for screen analysis"
        )
        REASONING_MODEL: str = Field(
            default="llama3-8b",
            description="Reasoning model for planning"
        )
        CODE_MODEL: str = Field(
            default="phind-codellama",
            description="Code generation model"
        )
        ENABLE_LOGGING: bool = Field(
            default=True,
            description="Log routing decisions"
        )
    
    def __init__(self):
        self.name = "AlphaOmega Router"
        self.valves = self.Valves()
        self.id = "alphaomega_router"
        self.type = "manifold"
        
    def pipes(self) -> List[dict]:
        """Available backend options"""
        return [
            {"id": "vision", "name": f"Vision ({self.valves.VISION_MODEL})"},
            {"id": "reasoning", "name": f"Reasoning ({self.valves.REASONING_MODEL})"},
            {"id": "code", "name": f"Code ({self.valves.CODE_MODEL})"},
            {"id": "agent", "name": "Computer Use (Agent-S)"},
            {"id": "image", "name": "Image Generation (ComfyUI)"},
            {"id": "mcp", "name": "Tools (MCP)"},
        ]
    
    def _detect_intent(self, message: str) -> str:
        """Detect user intent from message content"""
        message_lower = message.lower()
        
        # Image generation keywords
        image_keywords = [
            "generate image", "create image", "draw", "render", "paint",
            "picture of", "illustration", "artwork", "sdxl", "flux",
            "generate a photo", "make an image", "visualize"
        ]
        if any(kw in message_lower for kw in image_keywords):
            return "image"
        
        # Computer use keywords
        computer_keywords = [
            "screenshot", "screen", "click", "type", "press",
            "open app", "close window", "launch", "mouse", "keyboard",
            "what's on my screen", "find window", "desktop",
            "what can you see on", "show me my", "take a picture of my screen"
        ]
        if any(kw in message_lower for kw in computer_keywords):
            return "agent"
        
        # MCP tool keywords
        mcp_keywords = [
            "create artifact", "save artifact", "artifact",
            "save to memory", "remember this", "store this",
            "read file", "write file", "list files", "file operation"
        ]
        if any(kw in message_lower for kw in mcp_keywords):
            return "mcp"
        
        # Vision analysis keywords (but not computer use)
        vision_keywords = [
            "analyze this image", "what's in this image", "describe image",
            "look at this", "vision", "see this", "examine image"
        ]
        if any(kw in message_lower for kw in vision_keywords):
            return "vision"
        
        # Code generation keywords
        code_keywords = [
            "write code", "write a function", "write a script",
            "implement", "code for", "python code", "javascript",
            "create a class", "algorithm", "debug this code",
            "refactor", "optimize code"
        ]
        if any(kw in message_lower for kw in code_keywords):
            return "code"
        
        # Default to reasoning
        return "reasoning"
    
    async def pipe(
        self,
        body: Dict[str, Any],
        __user__: Optional[Dict[str, Any]] = None,
        __event_emitter__: Any = None
    ) -> AsyncGenerator[str, None]:
        """Main routing logic with streaming support"""
        
        try:
            # Extract message
            messages = body.get("messages", [])
            if not messages:
                yield "Error: No messages provided"
                return
            
            user_message = messages[-1].get("content", "")
            
            # Detect intent
            intent = self._detect_intent(user_message)
            
            # Log routing decision
            if self.valves.ENABLE_LOGGING:
                self._log_routing(intent, user_message, __user__)
            
            # Emit status
            if __event_emitter__:
                await __event_emitter__({
                    "type": "status",
                    "data": {
                        "description": f"Routing to {intent}...",
                        "done": False
                    }
                })
            
            # Route to appropriate backend
            if intent == "image":
                async for chunk in self._route_to_comfyui(user_message, messages, __event_emitter__):
                    yield chunk
            elif intent == "agent":
                async for chunk in self._route_to_agent_s(user_message, messages, __event_emitter__):
                    yield chunk
            elif intent == "mcp":
                async for chunk in self._route_to_mcp(user_message, messages, __event_emitter__):
                    yield chunk
            elif intent == "vision":
                async for chunk in self._route_to_ollama(
                    user_message, messages, self.valves.VISION_MODEL,
                    self.valves.OLLAMA_VISION_HOST, __event_emitter__
                ):
                    yield chunk
            elif intent == "code":
                async for chunk in self._route_to_ollama(
                    user_message, messages, self.valves.CODE_MODEL,
                    self.valves.OLLAMA_REASONING_HOST, __event_emitter__
                ):
                    yield chunk
            else:  # reasoning
                async for chunk in self._route_to_ollama(
                    user_message, messages, self.valves.REASONING_MODEL,
                    self.valves.OLLAMA_REASONING_HOST, __event_emitter__
                ):
                    yield chunk
                    
        except Exception as e:
            error_msg = f"Error in pipeline: {str(e)}"
            print(error_msg)
            yield error_msg
    
    async def _route_to_ollama(
        self,
        message: str,
        messages: List[Dict],
        model: str,
        host: str,
        event_emitter: Any = None
    ) -> AsyncGenerator[str, None]:
        """Route to Ollama for LLM inference with streaming"""
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{host}/api/chat",
                    json={
                        "model": model,
                        "messages": messages,
                        "stream": True
                    },
                    timeout=120.0
                )
                
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "message" in data:
                                content = data["message"].get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            yield f"\n\n[Error communicating with Ollama ({model}): {str(e)}]"
    
    async def _route_to_comfyui(
        self,
        message: str,
        messages: List[Dict],
        event_emitter: Any = None
    ) -> AsyncGenerator[str, None]:
        """Route to ComfyUI for image generation"""
        
        try:
            if event_emitter:
                await event_emitter({
                    "type": "status",
                    "data": {"description": "Generating image with ComfyUI...", "done": False}
                })
            
            prompt = self._extract_image_prompt(message)
            
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(
                    f"{self.valves.COMFYUI_HOST}/api/generate",
                    json={"prompt": prompt},
                    timeout=180.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    image_url = result.get("image_url", "")
                    
                    if image_url:
                        yield f"✅ Image generated successfully!\n\n"
                        yield f"Prompt: {prompt}\n\n"
                        yield f"![Generated Image]({image_url})"
                    else:
                        yield "Image generated but URL not available."
                else:
                    yield f"ComfyUI error: {response.status_code}"
                    
        except httpx.ConnectError:
            yield "⚠️ ComfyUI service is not available. Please ensure ComfyUI is running."
        except Exception as e:
            yield f"Error generating image: {str(e)}"
    
    async def _route_to_agent_s(
        self,
        message: str,
        messages: List[Dict],
        event_emitter: Any = None
    ) -> AsyncGenerator[str, None]:
        """Route to Agent-S for computer use automation"""
        
        try:
            if event_emitter:
                await event_emitter({
                    "type": "status",
                    "data": {"description": "Executing computer use action...", "done": False}
                })
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.valves.AGENT_S_HOST}/action",
                    json={
                        "prompt": message,
                        "messages": messages,
                        "safe_mode": True
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Stream response
                    yield result.get("response", "Action completed")
                    
                    # Add screenshot if available
                    if "screenshot" in result and result["screenshot"]:
                        yield f"\n\n📸 Screenshot:\n![Screen]({result['screenshot']})"
                    
                    # Add actions taken
                    if "actions_taken" in result and result["actions_taken"]:
                        yield "\n\n**Actions taken:**\n"
                        for action in result["actions_taken"]:
                            yield f"- {action}\n"
                            
                elif response.status_code == 403:
                    yield "⚠️ Action blocked by safety validator."
                else:
                    yield f"Agent-S error: {response.status_code}"
                    
        except httpx.ConnectError:
            yield "⚠️ Agent-S service is not available. Please ensure Agent-S is running."
        except Exception as e:
            yield f"Error executing action: {str(e)}"
    
    async def _route_to_mcp(
        self,
        message: str,
        messages: List[Dict],
        event_emitter: Any = None
    ) -> AsyncGenerator[str, None]:
        """Route to MCP server for tool use"""
        
        try:
            if event_emitter:
                await event_emitter({
                    "type": "status",
                    "data": {"description": "Executing MCP tool...", "done": False}
                })
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.valves.MCP_HOST}/execute",
                    json={
                        "prompt": message,
                        "messages": messages
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    yield result.get("response", "MCP action completed")
                    
                    if "artifact_url" in result:
                        yield f"\n\n📦 Artifact created: {result['artifact_url']}"
                else:
                    yield f"MCP error: {response.status_code}"
                    
        except httpx.ConnectError:
            yield "⚠️ MCP server is not available."
        except Exception as e:
            yield f"Error executing MCP tool: {str(e)}"
    
    def _extract_image_prompt(self, message: str) -> str:
        """Extract clean prompt from image generation request"""
        prefixes = [
            "generate image of ", "create image of ", "draw ", "draw me ",
            "make a picture of ", "generate ", "create ", "render ",
            "make an image of ", "paint "
        ]
        
        prompt = message
        for prefix in prefixes:
            if prompt.lower().startswith(prefix):
                prompt = prompt[len(prefix):].strip()
                break
        
        return prompt
    
    def _log_routing(self, intent: str, message: str, user: Optional[Dict] = None):
        """Log routing decisions for debugging"""
        try:
            log_dir = "/app/backend/data/logs"
            os.makedirs(log_dir, exist_ok=True)
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "intent": intent,
                "message_preview": message[:100],
                "user": user.get("email", "unknown") if user else "unknown"
            }
            
            with open(f"{log_dir}/routing.log", "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
            pass  # Don't fail on logging errors
