"""
ComfyUI API Wrapper for AlphaOmega
Provides simplified interface for image generation workflows
"""
import httpx
import json
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger("comfyui_bridge")


class ComfyUIClient:
    """Client for ComfyUI API"""
    
    def __init__(self, host: str = "http://localhost:8188"):
        self.host = host.rstrip("/")
        self.client = httpx.AsyncClient(timeout=180.0)
        self.workflows_dir = Path(__file__).parent / "workflows"
        logger.info(f"ComfyUIClient initialized for {self.host}")
    
    async def generate_image(
        self,
        prompt: str,
        workflow: str = "sdxl_default",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate image using ComfyUI workflow
        
        Args:
            prompt: Text prompt for image generation
            workflow: Workflow name (default: sdxl_default)
            **kwargs: Additional workflow parameters
            
        Returns:
            Dictionary with image URL and generation details
        """
        try:
            # Load workflow definition
            workflow_path = self.workflows_dir / f"{workflow}.json"
            
            if not workflow_path.exists():
                # Use basic workflow as fallback
                workflow_data = self._create_basic_workflow(prompt)
            else:
                with open(workflow_path) as f:
                    workflow_data = json.load(f)
                # Inject prompt into workflow
                workflow_data = self._inject_prompt(workflow_data, prompt)
            
            # Submit workflow to ComfyUI
            logger.info(f"Generating image with workflow: {workflow}")
            
            response = await self.client.post(
                f"{self.host}/prompt",
                json={"prompt": workflow_data}
            )
            
            response.raise_for_status()
            result = response.json()
            
            prompt_id = result.get("prompt_id")
            
            # Wait for completion (simplified - should use websocket in production)
            image_path = await self._wait_for_completion(prompt_id)
            
            return {
                "success": True,
                "image_url": image_path,
                "prompt_id": prompt_id,
                "workflow": workflow
            }
            
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_basic_workflow(self, prompt: str) -> Dict:
        """Create a basic SDXL workflow"""
        # Simplified workflow structure
        # In production, this would be a complete ComfyUI workflow JSON
        return {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}
            },
            "2": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": prompt, "clip": ["1", 1]}
            },
            "3": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": 1024, "height": 1024, "batch_size": 1}
            },
            "4": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": 42,
                    "steps": 20,
                    "cfg": 8.0,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["1", 0],
                    "positive": ["2", 0],
                    "negative": ["5", 0],
                    "latent_image": ["3", 0]
                }
            },
            "5": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": "low quality, blurry", "clip": ["1", 1]}
            },
            "6": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["4", 0], "vae": ["1", 2]}
            },
            "7": {
                "class_type": "SaveImage",
                "inputs": {"filename_prefix": "AlphaOmega", "images": ["6", 0]}
            }
        }
    
    def _inject_prompt(self, workflow: Dict, prompt: str) -> Dict:
        """Inject prompt into workflow JSON"""
        # Find CLIP text encode node and update prompt
        for node_id, node in workflow.items():
            if node.get("class_type") == "CLIPTextEncode":
                if "positive" in str(node.get("_meta", {})) or "inputs" in node:
                    node["inputs"]["text"] = prompt
                    break
        return workflow
    
    async def _wait_for_completion(self, prompt_id: str, timeout: int = 180) -> str:
        """Wait for ComfyUI to complete image generation"""
        # Simplified version - should use websocket for real-time updates
        # For now, just construct the expected output path
        output_dir = os.getenv("COMFYUI_OUTPUT_DIR", "./comfyui_bridge/output")
        
        # Return expected path (ComfyUI saves as AlphaOmega_XXXXX.png)
        return f"{self.host}/view?filename=AlphaOmega_{prompt_id}.png"
    
    async def list_models(self) -> Dict[str, Any]:
        """List available models in ComfyUI"""
        try:
            response = await self.client.get(f"{self.host}/object_info")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return {"error": str(e)}
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        try:
            response = await self.client.get(f"{self.host}/queue")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting queue status: {e}")
            return {"error": str(e)}
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
