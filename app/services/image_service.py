import asyncio
from urllib.parse import quote
class ImageService:
    def __init__(self):
        pass
    async def generate_image(self, prompt: str) -> dict:
        encoded_prompt = quote(prompt)
        # Using picsum with seed for random images based on prompt
        seed = abs(hash(prompt)) % 10000
        image_url = f"https://picsum.photos/seed/{seed}/500/500"
        
        return {
            "success": True,
            "image_url": image_url,
            "prompt": prompt,
            "model": "picsum",
            "status": "completed"
        }
    def generate_image_sync(self, prompt: str) -> dict:
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(self.generate_image(prompt))
image_service = ImageService()