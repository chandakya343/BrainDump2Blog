import pytest
from unittest.mock import Mock, patch
from src.idea2draft2 import ThoughtProcessor, MemoryObject
from datetime import datetime

@pytest.fixture
def mock_genai():
    with patch('google.generativeai') as mock:
        yield mock

@pytest.fixture
def processor(mock_genai):
    return ThoughtProcessor("dummy_api_key")

def test_memory_object_initialization():
    memory = MemoryObject()
    assert memory.interactions == []

def test_memory_object_add_interaction():
    memory = MemoryObject()
    test_response = "Test response"
    memory.add_interaction(test_response)
    assert len(memory.interactions) == 1
    assert "Test response" in memory.interactions[0]

def test_thought_processor_initialization(processor):
    assert processor.current_narrative == ""
    assert processor.current_growth_points == ""
    assert isinstance(processor.memory, MemoryObject)

def test_process_brain_dump(processor, mock_genai):
    # Mock response from the AI model
    mock_response = Mock()
    mock_response.text = """
<connected_narrative>
Test narrative
</connected_narrative>

<growth_points>
Test growth points
</growth_points>

<ai_contributions>
Test contributions
</ai_contributions>
"""
    processor.model.generate_content.return_value = mock_response

    # Test processing
    result = processor.process_brain_dump("Test brain dump")
    
    assert "Test narrative" in result["connected_narrative"]
    assert "Test growth points" in result["growth_points"]
    assert "Test contributions" in result["ai_contributions"]

def test_refine_narrative(processor, mock_genai):
    # Set initial state
    processor.current_narrative = "Initial narrative"
    processor.current_growth_points = "Initial growth points"

    # Mock response
    mock_response = Mock()
    mock_response.text = """
<connected_narrative>
Refined narrative
</connected_narrative>

<growth_points>
Refined growth points
</growth_points>

<ai_contributions>
Refined contributions
</ai_contributions>
"""
    processor.model.generate_content.return_value = mock_response

    # Test refinement
    result = processor.refine_narrative("Test refinement")
    
    assert "Refined narrative" in result["connected_narrative"]
    assert "Refined growth points" in result["growth_points"]
    assert "Refined contributions" in result["ai_contributions"]

def test_export_final_narrative(processor, tmp_path):
    # Set some test content
    processor.current_narrative = "Test narrative"
    processor.current_growth_points = "Test growth points"
    
    # Create temporary file path
    test_file = tmp_path / "test_export.json"
    
    # Export
    processor.export_final_narrative(str(test_file))
    
    # Verify file exists and content
    assert test_file.exists()
    content = test_file.read_text()
    assert "Test narrative" in content
    assert "Test growth points" in content