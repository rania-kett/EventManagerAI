"""
test_ai_service.py — Gemini AI service and API tests.
"""

from unittest.mock import MagicMock, patch

import pytest

from services.ai_service import AIService, AIServiceError, AIServiceNotConfiguredError


def test_not_configured_raises():
    ai = AIService(api_key="")
    assert ai.is_configured() is False
    with pytest.raises(AIServiceNotConfiguredError):
        ai.generate_event_description("Gala 2026")


def test_empty_title_raises():
    ai = AIService(api_key="test-key")
    with pytest.raises(AIServiceError):
        ai.generate_event_description("   ")


@patch("services.ai_service.genai")
def test_generate_event_description_success(mock_genai):
    mock_model = MagicMock()
    mock_model.generate_content.return_value = MagicMock(
        text="Une soirée exceptionnelle vous attend."
    )
    mock_genai.GenerativeModel.return_value = mock_model

    ai = AIService(api_key="test-key", model="gemini-2.0-flash")
    result = ai.generate_event_description(
        title="Gala Premium",
        location="Casablanca",
        category="Gala",
    )

    assert "exceptionnelle" in result
    mock_genai.configure.assert_called_once_with(api_key="test-key")
    mock_genai.GenerativeModel.assert_called_once_with("gemini-2.0-flash")


@pytest.fixture
def app():
    from app import create_app

    return create_app("testing")


@pytest.fixture
def client(app):
    return app.test_client()


def test_ai_generate_route_requires_title(client):
    response = client.post(
        "/events/ai/generate-description",
        json={"title": ""},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400


@patch("routes.event_routes.AIService")
def test_ai_generate_route_success(mock_ai_cls, client):
    mock_instance = MagicMock()
    mock_instance.generate_event_description.return_value = "Description IA générée."
    mock_ai_cls.from_config.return_value = mock_instance

    response = client.post(
        "/events/ai/generate-description",
        json={"title": "Conférence Tech"},
        headers={"Content-Type": "application/json"},
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["description"] == "Description IA générée."


def test_add_form_shows_generate_button(client):
    response = client.get("/events/add")
    html = response.data.decode("utf-8")

    assert "Générer la description" in html
    assert "js-generate-description" in html
    assert "ai-generate.js" in html
