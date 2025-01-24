import pytest
from unittest.mock import Mock, patch
from src.orchestrator import Orchestrator
from fastapi.testclient import TestClient
from src.orchestrator import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_orchestrator():
    with patch('src.orchestrator.Orchestrator') as mock:
        yield mock

def test_process_initial_idea(client, mock_orchestrator):
    # Mock response data
    mock_response = {
        "connected_narrative": "Test narrative",
        "growth_points": "Test growth points",
        "ai_contributions": "Test contributions"
    }
    
    # Configure mock
    mock_orchestrator.return_value.process_initial_idea.return_value = mock_response
    
    # Test API endpoint
    response = client.post(
        "/process",
        json={"idea": "Test idea"}
    )
    
    assert response.status_code == 200
    assert response.json() == mock_response

def test_refine_content(client, mock_orchestrator):
    # Mock response data
    mock_response = {
        "connected_narrative": "Refined narrative",
        "growth_points": "Refined growth points",
        "ai_contributions": "Refined contributions"
    }
    
    # Configure mock
    mock_orchestrator.return_value.refine_content.return_value = mock_response
    
    # Test API endpoint
    response = client.post(
        "/refine",
        json={"refinement": "Test refinement"}
    )
    
    assert response.status_code == 200
    assert response.json() == mock_response

def test_finalize_to_blog(client, mock_orchestrator):
    # Mock response
    mock_orchestrator.return_value.finalize_to_blog.return_value = "Test blog post"
    
    # Test API endpoint
    response = client.post("/finalize")
    
    assert response.status_code == 200
    assert response.json() == {"blog_post": "Test blog post"}

def test_error_handling(client, mock_orchestrator):
    # Configure mock to raise an exception
    mock_orchestrator.return_value.process_initial_idea.side_effect = Exception("Test error")
    
    # Test error handling
    response = client.post(
        "/process",
        json={"idea": "Test idea"}
    )
    
    assert response.status_code == 500
    assert "Test error" in response.json()["detail"]

@pytest.fixture
def orchestrator():
    return Orchestrator()

def test_orchestrator_initialization(orchestrator):
    assert orchestrator.current_state is None

def test_orchestrator_process_initial_idea(orchestrator):
    # Mock ThoughtProcessor
    orchestrator.thought_processor.process_brain_dump = Mock(
        return_value={"test": "result"}
    )
    
    result = orchestrator.process_initial_idea("test idea")
    assert result == {"test": "result"}
    assert orchestrator.current_state == {"test": "result"}

def test_orchestrator_refine_content(orchestrator):
    # Mock ThoughtProcessor
    orchestrator.thought_processor.refine_narrative = Mock(
        return_value={"test": "refined"}
    )
    
    result = orchestrator.refine_content("test refinement")
    assert result == {"test": "refined"}
    assert orchestrator.current_state == {"test": "refined"}

def test_orchestrator_finalize_to_blog(orchestrator):
    # Set current state
    orchestrator.current_state = {"connected_narrative": "test narrative"}
    
    # Mock BlogConverter
    orchestrator.blog_converter.convert_draft = Mock(
        return_value="test blog post"
    )
    
    result = orchestrator.finalize_to_blog()
    assert result == "test blog post"

def test_orchestrator_finalize_without_state(orchestrator):
    with pytest.raises(ValueError):
        orchestrator.finalize_to_blog()