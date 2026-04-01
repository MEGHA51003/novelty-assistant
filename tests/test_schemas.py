import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from datetime import datetime


class TestAuthEndpoints:
    def test_register_validation(self):
        from pydantic import ValidationError
        from app.schemas.user import UserCreate

        with pytest.raises(ValidationError):
            UserCreate(email="invalid-email", password="short")

    def test_user_create_valid(self):
        from app.schemas.user import UserCreate

        user = UserCreate(
            email="test@example.com",
            name="Test User",
            password="securepassword123"
        )
        assert user.email == "test@example.com"
        assert user.name == "Test User"


class TestProjectSchemas:
    def test_project_create(self):
        from app.schemas.project import ProjectCreate

        project = ProjectCreate(
            title="Test Project",
            description="A test project",
            goals="Complete testing",
            reference_links=["https://example.com"],
            tags=["testing", "demo"]
        )
        assert project.title == "Test Project"
        assert len(project.reference_links) == 1

    def test_project_update_partial(self):
        from app.schemas.project import ProjectUpdate

        update = ProjectUpdate(title="Updated Title")
        data = update.model_dump(exclude_none=True)
        assert "title" in data
        assert "description" not in data


class TestConversationSchemas:
    def test_conversation_create(self):
        from app.schemas.conversation import ConversationCreate

        conv = ConversationCreate(title="My Conversation")
        assert conv.title == "My Conversation"

    def test_conversation_create_default(self):
        from app.schemas.conversation import ConversationCreate

        conv = ConversationCreate()
        assert conv.title is None


class TestMessageSchemas:
    def test_chat_request(self):
        from app.schemas.message import ChatRequest

        chat = ChatRequest(message="Hello, Claude!")
        assert chat.message == "Hello, Claude!"
        assert chat.image_url is None

    def test_chat_request_with_image(self):
        from app.schemas.message import ChatRequest

        chat = ChatRequest(
            message="What's in this image?",
            image_url="https://example.com/image.jpg"
        )
        assert chat.image_url == "https://example.com/image.jpg"


class TestMemorySchemas:
    def test_memory_create(self):
        from app.schemas.memory import MemoryCreate

        memory = MemoryCreate(
            memory_type="context",
            title="Project Context",
            content={"background": "Test background info"}
        )
        assert memory.memory_type == "context"
        assert memory.content["background"] == "Test background info"

    def test_memory_types(self):
        from app.schemas.memory import MemoryCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            MemoryCreate(
                memory_type="invalid_type",
                title="Test",
                content={}
            )


class TestAgentSchemas:
    def test_agent_execution_create(self):
        from app.schemas.agent import AgentExecutionCreate

        execution = AgentExecutionCreate(
            agent_type="memory_organizer",
            input_data={"project_id": "123"}
        )
        assert execution.agent_type == "memory_organizer"

    def test_agent_execution_response(self):
        from app.schemas.agent import AgentExecutionResponse

        response = AgentExecutionResponse(
            id="test-id",
            project_id="project-123",
            agent_type="memory_organizer",
            status="pending",
            input_data={},
            output_data={},
            error_message=None,
            started_at=None,
            completed_at=None,
            created_at=datetime.utcnow()
        )
        assert response.status == "pending"
        assert response.agent_type == "memory_organizer"
