"""
Vision Analysis using Ollama + LLaVA
Optimized for AMD MI50 GPU
"""
import ollama
from typing import Optional, Dict, Any
from pathlib import Path
import logging
from PIL import Image
import io
import base64

logger = logging.getLogger("agent_s.vision")


class VisionAnalyzer:
    """Analyze screenshots and images using LLaVA vision model via Ollama"""
    
    def __init__(
        self,
        ollama_host: str = "http://localhost:11434",
        model: str = "llava:34b"
    ):
        """
        Initialize vision analyzer
        
        Args:
            ollama_host: Ollama API endpoint (GPU 0 - MI50 #1)
            model: Vision model to use (default: llava:34b)
        """
        self.ollama_host = ollama_host
        self.model = model
        self.client = ollama.Client(host=ollama_host)
        
        logger.info(f"VisionAnalyzer initialized with {model} at {ollama_host}")
    
    async def analyze(
        self,
        image_path: str,
        prompt: str,
        context: Optional[str] = None,
        preprocess: bool = True
    ) -> str:
        """
        Analyze image with vision model
        
        Args:
            image_path: Path to screenshot or image file
            prompt: What to analyze or look for
            context: Additional context to help analysis
            preprocess: Whether to resize/optimize image first
            
        Returns:
            Analysis result as string
        """
        try:
            # Preprocess image if requested
            if preprocess:
                image_path = self._preprocess_image(image_path)
            
            # Build vision prompt
            vision_prompt = self._build_prompt(prompt, context)
            
            logger.debug(f"Analyzing image: {image_path}")
            logger.debug(f"Prompt: {vision_prompt[:100]}...")
            
            # Call Ollama with image
            response = self.client.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': vision_prompt,
                    'images': [image_path]
                }]
            )
            
            result = response['message']['content']
            logger.debug(f"Analysis result: {result[:100]}...")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in vision analysis: {e}")
            return f"Error analyzing image: {str(e)}"
    
    def analyze_region(
        self,
        image_path: str,
        x: int, y: int, w: int, h: int,
        prompt: str
    ) -> str:
        """
        Analyze specific region of screenshot for better accuracy
        
        Args:
            image_path: Path to full screenshot
            x, y: Top-left coordinates of region
            w, h: Width and height of region
            prompt: What to analyze in this region
            
        Returns:
            Analysis of the specific region
        """
        try:
            # Crop to region
            img = Image.open(image_path)
            region = img.crop((x, y, x+w, y+h))
            
            # Save temporary region file
            region_path = f"/tmp/region_{x}_{y}_{w}_{h}.png"
            region.save(region_path, optimize=True)
            
            # Analyze cropped region
            result = self.analyze(
                image_path=region_path,
                prompt=prompt,
                preprocess=False  # Already cropped
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing region: {e}")
            return f"Error analyzing region: {str(e)}"
    
    def _build_prompt(self, prompt: str, context: Optional[str] = None) -> str:
        """Build effective vision prompt"""
        
        base_prompt = """You are analyzing a computer screen to help with automation.
Be specific about:
- Applications and windows visible
- UI elements (buttons, menus, text fields)
- Text content you can read
- Positions of key elements (top-left, center, etc.)
- Current state (focused window, dialog boxes, etc.)

"""
        
        if context:
            base_prompt += f"Context: {context}\n\n"
        
        base_prompt += f"Task: {prompt}"
        
        return base_prompt
    
    def _preprocess_image(self, image_path: str) -> str:
        """
        Preprocess image for better analysis
        - Resize if too large (faster inference)
        - Optimize quality
        """
        try:
            import os
            
            img = Image.open(image_path)
            original_size = img.size
            
            # Get max dimensions from env or defaults
            max_width = int(os.getenv("SCREENSHOT_MAX_WIDTH", 1280))
            max_height = int(os.getenv("SCREENSHOT_MAX_HEIGHT", 720))
            
            # Resize if needed
            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                logger.debug(f"Resized image from {original_size} to {img.size}")
            
            # Save optimized version
            optimized_path = image_path.replace(".png", "_optimized.png")
            img.save(optimized_path, optimize=True, quality=85)
            
            return optimized_path
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed, using original: {e}")
            return image_path
    
    async def identify_ui_elements(
        self,
        image_path: str,
        element_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Identify UI elements in screenshot
        
        Args:
            image_path: Path to screenshot
            element_type: Optional filter (e.g., "buttons", "text_fields", "menus")
            
        Returns:
            Dictionary of identified elements with positions
        """
        
        prompt = f"List all UI elements you can see in this screenshot."
        if element_type:
            prompt += f" Focus specifically on {element_type}."
        
        prompt += """
For each element, describe:
1. Type (button, text field, menu, window, etc.)
2. Label or text if visible
3. Approximate position (top-left, center, bottom-right, etc.)

Format as a structured list."""
        
        result = await self.analyze(image_path, prompt)
        
        # Parse result into structured format
        # TODO: More sophisticated parsing
        return {
            "raw_analysis": result,
            "elements": self._parse_ui_elements(result)
        }
    
    def _parse_ui_elements(self, analysis: str) -> list:
        """Parse vision model output into structured UI elements"""
        # Simple parsing - will improve with better prompting
        elements = []
        
        lines = analysis.split('\n')
        for line in lines:
            line = line.strip()
            if line and any(kw in line.lower() for kw in ['button', 'menu', 'window', 'field', 'icon']):
                elements.append({
                    "description": line,
                    "type": "unknown"  # Would need better parsing
                })
        
        return elements
    
    async def find_element(
        self,
        image_path: str,
        element_description: str
    ) -> Dict[str, Any]:
        """
        Find specific UI element in screenshot
        
        Args:
            image_path: Path to screenshot
            element_description: Description of element to find (e.g., "Close button")
            
        Returns:
            Dictionary with element info and estimated position
        """
        
        prompt = f"""Find this UI element: {element_description}

If you can see it, describe:
1. Its exact location (provide approximate pixel position or quadrant)
2. What it looks like (color, size, text)
3. Its current state (enabled/disabled, highlighted, etc.)

If you cannot find it, say "NOT_FOUND"."""
        
        result = await self.analyze(image_path, prompt)
        
        found = "NOT_FOUND" not in result.upper()
        
        return {
            "found": found,
            "description": result,
            "element": element_description
        }
