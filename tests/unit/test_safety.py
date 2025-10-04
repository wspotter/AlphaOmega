"""
Unit tests for Safety Validator
"""
import pytest
from agent_s.safety.validator import SafetyValidator


@pytest.fixture
def validator():
    """Create SafetyValidator instance"""
    return SafetyValidator()


def test_validate_safe_actions(validator):
    """Test validation of safe actions"""
    actions = [
        {
            "type": "mouse",
            "params": {"action": "click", "x": 100, "y": 200},
            "description": "Click button"
        },
        {
            "type": "keyboard",
            "params": {"action": "type", "text": "Hello"},
            "description": "Type text"
        }
    ]
    
    result = validator.validate(actions)
    
    assert result["safe"] is True
    assert result["reason"] is None


def test_validate_dangerous_command(validator):
    """Test blocking of dangerous system commands"""
    actions = [
        {
            "type": "system_command",
            "params": {"command": "rm -rf /"},
            "description": "Delete system"
        }
    ]
    
    # Force allow system commands for this test
    validator.allow_system_commands = True
    
    result = validator.validate(actions)
    
    assert result["safe"] is False
    assert "dangerous" in result["reason"].lower()


def test_validate_file_write_disabled(validator):
    """Test file write when disabled"""
    validator.allow_file_write = False
    
    actions = [
        {
            "type": "file_write",
            "params": {"path": "/tmp/test.txt", "content": "test"},
            "description": "Write file"
        }
    ]
    
    result = validator.validate(actions)
    
    assert result["safe"] is False
    assert "disabled" in result["reason"].lower()


def test_validate_dangerous_keyboard(validator):
    """Test detection of dangerous keyboard shortcuts"""
    actions = [
        {
            "type": "keyboard",
            "params": {"action": "hotkey", "keys": ["ctrl", "alt", "delete"]},
            "description": "Task manager"
        }
    ]
    
    result = validator.validate(actions)
    
    # Should pass but with warnings
    assert "warnings" in result
    if result["warnings"]:
        assert "risky" in result["warnings"][0].lower()


def test_is_dangerous_command(validator):
    """Test dangerous command detection"""
    dangerous_commands = [
        "rm -rf /",
        "dd if=/dev/zero of=/dev/sda",
        "mkfs.ext4 /dev/sda",
        ":(){ :|:& };:",
        "shutdown -h now"
    ]
    
    for cmd in dangerous_commands:
        assert validator._is_dangerous_command(cmd) is True
    
    safe_commands = [
        "ls -la",
        "cat file.txt",
        "echo 'Hello'"
    ]
    
    for cmd in safe_commands:
        assert validator._is_dangerous_command(cmd) is False


def test_path_validation(validator):
    """Test file path validation"""
    validator.allowed_paths = ["/tmp", "/home/.*/Downloads"]
    
    assert validator._is_path_allowed("/tmp/test.txt") is True
    assert validator._is_path_allowed("/home/user/Downloads/file.txt") is True
    assert validator._is_path_allowed("/etc/passwd") is False
    assert validator._is_path_allowed("/root/secret") is False
