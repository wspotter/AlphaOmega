"""
Agent-S Server - Computer Use Automation for AlphaOmega
Coordinates vision analysis, action planning, and execution
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
import logging
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_s.vision.analyzer import VisionAnalyzer
from agent_s.actions.screen import ScreenAction
from agent_s.actions.mouse import MouseAction
from agent_s.actions.keyboard import KeyboardAction
from agent_s.safety.validator import SafetyValidator
from agent_s.mcp.client import MCPClient

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(
    level=getattr(logging, os.getenv("AGENT_LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.getenv("AGENT_LOG_FILE", "logs/agent_actions.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("agent_s")

# Initialize FastAPI
app = FastAPI(
    title="Agent-S - AlphaOmega Computer Use",
    description="AI-powered computer automation with vision and safety",
    version="1.0.0"
)

# CORS for OpenWebUI integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
vision_analyzer = None
mcp_client = None
safety_validator = None
screen_action = None
mouse_action = None
keyboard_action = None


@app.on_event("startup")
async def startup_event():
    """Initialize all components on startup"""
    global vision_analyzer, mcp_client, safety_validator
    global screen_action, mouse_action, keyboard_action
    
    logger.info("Starting Agent-S server...")
    
    try:
        # Initialize vision analyzer
        vision_analyzer = VisionAnalyzer(
            ollama_host=os.getenv("OLLAMA_VISION_HOST", "http://localhost:11434"),
            model=os.getenv("VISION_MODEL", "llava:34b")
        )
        logger.info(f"Vision analyzer initialized with {os.getenv('VISION_MODEL', 'llava:34b')}")
        
        # Initialize MCP client
        mcp_client = MCPClient(
            server_url=os.getenv("MCP_SERVER_URL", "http://localhost:8002")
        )
        logger.info("MCP client initialized")
        
        # Initialize safety validator
        safety_validator = SafetyValidator()
        logger.info("Safety validator initialized")
        
        # Initialize action handlers
        screen_action = ScreenAction()
        mouse_action = MouseAction()
        keyboard_action = KeyboardAction()
        logger.info("Action handlers initialized")
        
        # Create screenshot directory
        screenshot_dir = os.getenv("SCREENSHOT_DIR", "/tmp/agent_screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        
        logger.info("Agent-S startup complete ✓")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


class ActionRequest(BaseModel):
    """Request model for computer use actions"""
    prompt: str = Field(..., description="User request describing the action")
    messages: Optional[List[Dict[str, Any]]] = Field(default=[], description="Chat history for context")
    safe_mode: bool = Field(default=True, description="Enable safety validation")
    include_screenshot: bool = Field(default=True, description="Include screenshot in response")


class ActionResponse(BaseModel):
    """Response model for executed actions"""
    response: str
    screenshot: Optional[str] = None
    actions_taken: List[str] = []
    artifacts: List[str] = []
    success: bool = True
    error: Optional[str] = None


@app.post("/action", response_model=ActionResponse)
async def execute_action(request: ActionRequest):
    """
    Main endpoint for computer use actions
    Analyzes screen, plans actions, validates safety, and executes
    """
    logger.info(f"Received action request: {request.prompt[:100]}...")
    
    try:
        # Step 1: Capture screenshot
        logger.info("Capturing screenshot...")
        screenshot_path = screen_action.capture()
        
        if not screenshot_path or not os.path.exists(screenshot_path):
            raise HTTPException(status_code=500, detail="Failed to capture screenshot")
        
        # Step 2: Analyze screen with vision model
        logger.info("Analyzing screenshot with vision model...")
        vision_analysis = await vision_analyzer.analyze(
            image_path=screenshot_path,
            prompt=f"Analyze this screen to help with: {request.prompt}"
        )
        
        logger.info(f"Vision analysis complete: {vision_analysis[:100]}...")
        
        # Step 3: Plan actions based on request and vision
        logger.info("Planning actions...")
        action_plan = await _plan_actions(
            prompt=request.prompt,
            vision_result=vision_analysis,
            messages=request.messages
        )
        
        # Step 4: Validate actions for safety
        if request.safe_mode:
            logger.info("Validating action safety...")
            validation_result = safety_validator.validate(action_plan)
            
            if not validation_result["safe"]:
                logger.warning(f"Action blocked: {validation_result['reason']}")
                return ActionResponse(
                    response=f"❌ Action blocked for safety: {validation_result['reason']}",
                    screenshot=screenshot_path if request.include_screenshot else None,
                    actions_taken=[],
                    success=False,
                    error=validation_result["reason"]
                )
        
        # Step 5: Execute approved actions
        logger.info(f"Executing {len(action_plan)} actions...")
        executed_actions = []
        artifacts = []
        
        for i, action in enumerate(action_plan):
            try:
                logger.info(f"Executing action {i+1}/{len(action_plan)}: {action.get('type')}")
                
                if action["type"] == "mouse":
                    mouse_action.execute(action["params"])
                    executed_actions.append(f"🖱️  {action['description']}")
                    
                elif action["type"] == "keyboard":
                    keyboard_action.execute(action["params"])
                    executed_actions.append(f"⌨️  {action['description']}")
                    
                elif action["type"] == "wait":
                    await asyncio.sleep(action["params"].get("duration", 1))
                    executed_actions.append(f"⏱️  {action['description']}")
                    
                elif action["type"] == "mcp_tool":
                    result = await mcp_client.execute_tool(
                        tool_name=action["tool"],
                        params=action["params"]
                    )
                    executed_actions.append(f"🔧 {action['description']}")
                    if "artifact_url" in result:
                        artifacts.append(result["artifact_url"])
                
                # Small delay between actions
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error executing action {i+1}: {e}")
                executed_actions.append(f"❌ Failed: {action['description']} - {str(e)}")
        
        # Step 6: Generate natural language response
        response_text = await _generate_response(
            prompt=request.prompt,
            vision_analysis=vision_analysis,
            actions_taken=executed_actions
        )
        
        logger.info("Action execution complete")
        
        return ActionResponse(
            response=response_text,
            screenshot=screenshot_path if request.include_screenshot else None,
            actions_taken=executed_actions,
            artifacts=artifacts,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Error in action execution: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/screenshot")
async def take_screenshot():
    """Simple endpoint to capture and return a screenshot"""
    try:
        screenshot_path = screen_action.capture()
        return {"screenshot_path": screenshot_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/screenshot/{filename}")
async def get_screenshot(filename: str):
    """Serve screenshot files"""
    screenshot_dir = os.getenv("SCREENSHOT_DIR", "/tmp/agent_screenshots")
    file_path = os.path.join(screenshot_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Screenshot not found")
    
    return FileResponse(file_path, media_type="image/png")


@app.get("/health")
async def health_check():
    """Health check endpoint with service status"""
    try:
        # Check MCP connection
        mcp_connected = await mcp_client.is_connected() if mcp_client else False
        
        # Check if we can capture screenshots
        can_capture = screen_action is not None
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "vision": vision_analyzer is not None,
                "mcp": mcp_connected,
                "screen_capture": can_capture,
                "mouse": mouse_action is not None,
                "keyboard": keyboard_action is not None
            },
            "config": {
                "vision_model": os.getenv("VISION_MODEL", "llava:34b"),
                "safe_mode": os.getenv("AGENT_SAFE_MODE", "true"),
                "ollama_host": os.getenv("OLLAMA_VISION_HOST", "http://localhost:11434")
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )


async def _plan_actions(
    prompt: str,
    vision_result: str,
    messages: List[Dict]
) -> List[Dict[str, Any]]:
    """
    Plan actions based on user prompt and vision analysis
    Returns list of actions to execute
    """
    # For now, return simple action based on keywords
    # TODO: Use reasoning model to intelligently plan multi-step actions
    
    actions = []
    prompt_lower = prompt.lower()
    
    # Simple keyword-based planning (will be replaced with LLM planning)
    if "screenshot" in prompt_lower or "what's on" in prompt_lower:
        # Just analyze, no actions needed
        actions.append({
            "type": "wait",
            "params": {"duration": 0},
            "description": "Screen analysis only"
        })
    
    elif "click" in prompt_lower:
        # Extract coordinates or element (simplified)
        actions.append({
            "type": "mouse",
            "params": {"action": "click", "x": 500, "y": 500},
            "description": "Click at detected location"
        })
    
    return actions


async def _generate_response(
    prompt: str,
    vision_analysis: str,
    actions_taken: List[str]
) -> str:
    """Generate natural language response to user"""
    
    if not actions_taken or actions_taken[0].startswith("⏱️  Screen analysis"):
        # No actions, just vision analysis
        return f"I can see your screen. Here's what I found:\n\n{vision_analysis}"
    
    # Actions were taken
    response = f"I've analyzed your screen and completed the requested actions:\n\n"
    response += f"**Screen Analysis:**\n{vision_analysis}\n\n"
    response += f"**Actions Completed:**\n"
    for action in actions_taken:
        response += f"- {action}\n"
    
    return response


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("AGENT_S_PORT", 8001))
    
    logger.info(f"Starting Agent-S server on port {port}...")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level=os.getenv("AGENT_LOG_LEVEL", "info").lower()
    )
