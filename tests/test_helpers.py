import pytest
from datetime import datetime, timedelta
from jose import jwt


class TestJWTHelpers:
    def test_create_access_token(self):
        from app.utils.helpers import create_access_token

        token = create_access_token(data={"sub": "user-123"})
        assert token is not None
        assert isinstance(token, str)

    def test_decode_valid_token(self):
        from app.utils.helpers import create_access_token, decode_token

        token = create_access_token(data={"sub": "user-123"})
        payload = decode_token(token)

        assert payload is not None
        assert payload["sub"] == "user-123"

    def test_decode_invalid_token(self):
        from app.utils.helpers import decode_token

        payload = decode_token("invalid-token")
        assert payload is None


class TestPasswordHelpers:
    def test_password_hash_and_verify(self):
        from app.utils.helpers import get_password_hash, verify_password

        password = "securepassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False


class TestConfig:
    def test_settings_load(self):
        from app.config import settings

        assert hasattr(settings, "SUPABASE_URL")
        assert hasattr(settings, "ANTHROPIC_API_KEY")
        assert hasattr(settings, "GEMINI_API_KEY")
