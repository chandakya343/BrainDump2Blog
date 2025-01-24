import pytest
from unittest.mock import Mock, patch
from src.Draft2Blog import Draft2Blog, BlogConfig, BlogMemory
import json

@pytest.fixture
def mock_genai():
    with patch('google.generativeai') as mock:
        yield mock

@pytest.fixture
def converter(mock_genai):
    return Draft2Blog("dummy_api_key")

def test_blog_memory_initialization():
    memory = BlogMemory()
    assert memory.drafts == []

def test_blog_memory_add_draft():
    memory = BlogMemory()
    memory.add_draft("original", "styled")
    assert len(memory.drafts) == 1
    assert memory.drafts[0]["original_draft"] == "original"
    assert memory.drafts[0]["styled_draft"] == "styled"

def test_blog_config_defaults():
    config = BlogConfig()
    assert config.temperature == 0.7
    assert config.top_p == 0.95
    assert config.top_k == 64
    assert config.max_output_tokens == 8192
    assert config.model_name == "gemini-exp-1206"

def test_draft2blog_initialization(converter):
    assert isinstance(converter.config, BlogConfig)
    assert isinstance(converter.memory, BlogMemory)

def test_convert_draft(converter, mock_genai):
    # Mock chat response
    mock_chat = Mock()
    mock_chat.send_message.return_value.text = "<styled_draft>Test styled content</styled_draft>"
    converter.chat = mock_chat

    # Test conversion
    result = converter.convert_draft("Test draft")
    assert result == "Test styled content"
    
    # Verify memory storage
    assert len(converter.memory.drafts) == 1
    assert "Test draft" in converter.memory.drafts[0]["original_draft"]

def test_convert_draft_with_existing_tags(converter, mock_genai):
    # Mock chat response
    mock_chat = Mock()
    mock_chat.send_message.return_value.text = "<styled_draft>Test styled content</styled_draft>"
    converter.chat = mock_chat

    # Test conversion with pre-wrapped content
    result = converter.convert_draft("<draft>Test draft</draft>")
    assert result == "Test styled content"

def test_export_history(converter, tmp_path):
    # Add some test drafts
    converter.memory.add_draft("original1", "styled1")
    converter.memory.add_draft("original2", "styled2")
    
    # Create temporary file path
    test_file = tmp_path / "test_history.json"
    
    # Export
    converter.export_history(str(test_file))
    
    # Verify file exists and content
    assert test_file.exists()
    with open(test_file) as f:
        content = json.load(f)
    assert len(content["drafts"]) == 2
    assert content["drafts"][0]["original_draft"] == "original1"
    assert content["drafts"][1]["styled_draft"] == "styled2"

def test_error_handling(converter, mock_genai):
    # Mock chat response without required tags
    mock_chat = Mock()
    mock_chat.send_message.return_value.text = "Invalid response without tags"
    converter.chat = mock_chat

    # Test error handling
    with pytest.raises(ValueError):
        converter.convert_draft("Test draft")