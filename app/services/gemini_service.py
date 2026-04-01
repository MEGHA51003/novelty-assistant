import google.generativeai as genai
from typing import Optional
from app.config import settings


class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def analyze_image(
        self,
        image_url: str,
        question: Optional[str] = None
    ) -> str:
        try:
            import httpx
            response = httpx.get(image_url, timeout=30)
            response.raise_for_status()
            image_data = response.content

            if question:
                prompt = f"""Analyze this image and answer the following question: {question}

Provide a detailed response based on the image content."""
            else:
                prompt = """Analyze this image in detail. Describe:
1. What you see in the image
2. Key objects or elements present
3. Any text or labels visible
4. Overall context and purpose of the image

Be thorough and descriptive in your analysis."""

            image_part = {
                "mime_type": "image/jpeg",
                "data": image_data
            }

            response = self.model.generate_content([prompt, image_part])
            return response.text

        except Exception as e:
            return f"Error analyzing image: {str(e)}"

    def analyze_image_sync(
        self,
        image_url: str,
        question: Optional[str] = None
    ) -> str:
        try:
            import httpx
            response = httpx.get(image_url, timeout=30)
            response.raise_for_status()
            image_data = response.content

            if question:
                prompt = f"""Analyze this image and answer the following question: {question}

Provide a detailed response based on the image content."""
            else:
                prompt = """Analyze this image in detail. Describe:
1. What you see in the image
2. Key objects or elements present
3. Any text or labels visible
4. Overall context and purpose of the image

Be thorough and descriptive in your analysis."""

            image_part = {
                "mime_type": "image/jpeg",
                "data": image_data
            }

            response = self.model.generate_content([prompt, image_part])
            return response.text

        except Exception as e:
            return f"Error analyzing image: {str(e)}"


gemini_service = GeminiService()
