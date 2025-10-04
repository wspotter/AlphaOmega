"""
Unit tests for Vision Analyzer
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from agent_s.vision.analyzer import VisionAnalyzer


@pytest.fixture
def vision_analyzer():
    """Create VisionAnalyzer instance for testing"""
    return VisionAnalyzer(
        ollama_host="http://localhost:11434",
        model="llava:34b"
    )


@pytest.mark.asyncio
async def test_analyze_screenshot(vision_analyzer, tmp_path):
    """Test screenshot analysis"""
    # Create test image
    from PIL import Image
    test_image = Image.new('RGB', (800, 600), color='white')
    image_path = tmp_path / "test_screen.png"
    test_image.save(image_path)
    
    # Mock Ollama response
    with patch.object(vision_analyzer.client, 'chat') as mock_chat:
        mock_chat.return_value = {
            'message': {
                'content': 'Test screen with white background'
            }
        }
        
        result = await vision_analyzer.analyze(
            image_path=str(image_path),
            prompt="What do you see?"
        )
        
        assert "Test screen" in result
        mock_chat.assert_called_once()


def test_analyze_region(vision_analyzer, tmp_path):
    """Test region analysis"""
    from PIL import Image
    
    # Create test image
    test_image = Image.new('RGB', (800, 600), color='blue')
    image_path = tmp_path / "test_screen.png"
    test_image.save(image_path)
    
    # Mock Ollama response
    with patch.object(vision_analyzer.client, 'chat') as mock_chat:
        mock_chat.return_value = {
            'message': {
                'content': 'Blue region detected'
            }
        }
        
        result = vision_analyzer.analyze_region(
            image_path=str(image_path),
            x=100, y=100, w=200, h=200,
            prompt="What color is this?"
        )
        
        assert "Blue" in result


def test_preprocess_image(vision_analyzer, tmp_path):
    """Test image preprocessing"""
    from PIL import Image
    
    # Create large test image
    large_image = Image.new('RGB', (2560, 1440), color='red')
    image_path = tmp_path / "large_screen.png"
    large_image.save(image_path)
    
    # Preprocess
    processed_path = vision_analyzer._preprocess_image(str(image_path))
    
    # Check that image was resized
    processed_image = Image.open(processed_path)
    assert processed_image.width <= 1280
    assert processed_image.height <= 720


@pytest.mark.asyncio
async def test_identify_ui_elements(vision_analyzer, tmp_path):
    """Test UI element identification"""
    from PIL import Image
    
    test_image = Image.new('RGB', (800, 600), color='white')
    image_path = tmp_path / "test_ui.png"
    test_image.save(image_path)
    
    with patch.object(vision_analyzer.client, 'chat') as mock_chat:
        mock_chat.return_value = {
            'message': {
                'content': '''
                1. Button: "Submit" - center of screen
                2. Text field: "Username" - top-left
                3. Menu: "File" - top menu bar
                '''
            }
        }
        
        result = await vision_analyzer.identify_ui_elements(str(image_path))
        
        assert "raw_analysis" in result
        assert "elements" in result
        assert len(result["elements"]) > 0
