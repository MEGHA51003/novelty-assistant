import pytest


class TestImageServiceMock:
    def test_mock_generate(self):
        from app.services.image_service import ImageService
        import asyncio

        service = ImageService()
        service.use_mock = True

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            service.generate_image("A beautiful sunset")
        )
        loop.close()

        assert result["success"] is True
        assert "image_url" in result
        assert result["model"] == "mock"
        assert result["status"] == "completed"
