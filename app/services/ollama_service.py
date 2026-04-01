import requests
import json
from typing import Optional, List, Dict, Any
from app.config import settings
class OllamaService:
    def __init__(self):
        self.base_url = "http://localhost:11434/api"
        self.model = settings.OLLAMA_MODEL if hasattr(settings, 'OLLAMA_MODEL') else "llama3.2"
        self.use_mock = not self._check_connection()
    def _check_connection(self) -> bool:
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "read_memory",
                "description": "Read memory entries from the project knowledge base",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "memory_type": {
                            "type": "string",
                            "enum": ["context", "decisions", "todos", "facts", "concepts"]
                        },
                        "project_id": {"type": "string"}
                    },
                    "required": ["project_id"]
                }
            },
            {
                "name": "write_memory",
                "description": "Write a new memory entry to the project knowledge base",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "memory_type": {"type": "string"},
                        "title": {"type": "string"},
                        "content": {"type": "object"},
                        "project_id": {"type": "string"}
                    },
                    "required": ["memory_type", "title", "content", "project_id"]
                }
            },
            {
                "name": "analyze_image",
                "description": "Analyze an image using AI vision",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "image_url": {"type": "string"},
                        "question": {"type": "string"}
                    },
                    "required": ["image_url"]
                }
            }
        ]
    def build_system_prompt(self, project: Dict[str, Any], memory_context: str = "") -> str:
        brief = f"""You are an AI assistant helping with a project.
Project: {project.get('title', 'Untitled')}
Description: {project.get('description', 'No description')}
Goals: {project.get('goals', 'No goals')}
Reference Links: {', '.join(project.get('reference_links', []) or ['None'])}
Tags: {', '.join(project.get('tags', []) or ['None'])}
"""
        if memory_context:
            brief += f"\nRelevant Project Memory:\n{memory_context}"
        brief += """
You have access to tools. When you need to use a tool, respond with this format:
[TOOL_CALL]
{"tool": "tool_name", "input": {"field": "value"}}
[/TOOL_CALL]
Available tools:
- read_memory: Read project memory (needs project_id)
- write_memory: Save to memory (needs project_id, memory_type, title, content)
- analyze_image: Analyze an image (needs image_url, optional question)
Example: [TOOL_CALL]
{"tool": "read_memory", "input": {"project_id": "abc123", "memory_type": "decisions"}}
[/TOOL_CALL]
Otherwise, respond normally to the user's message.
"""
        return brief
    def parse_tool_call(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse tool call from AI response"""
        try:
            # Look for [TOOL_CALL] markers
            if "[TOOL_CALL]" in response_text and "[/TOOL_CALL]" in response_text:
                start = response_text.find("[TOOL_CALL]") + len("[TOOL_CALL]")
                end = response_text.find("[/TOOL_CALL]")
                tool_json = response_text[start:end].strip()
                return json.loads(tool_json)
        except:
            pass
        return None
    def chat(self, messages: List[Dict[str, str]], system_prompt: str) -> Dict[str, Any]:
        if self.use_mock:
            return self._mock_response(messages)
        full_prompt = f"{system_prompt}\n\n"
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if isinstance(content, list):
                content = " ".join([c.get("text", "") for c in content if isinstance(c, dict)])
            full_prompt += f"{role.upper()}: {content}\n"
        full_prompt += "ASSISTANT:"
        try:
            response = requests.post(
                f"{self.base_url}/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 2048
                    }
                },
                timeout=120
            )
            if response.status_code == 200:
                result = response.json()
                return {
                    "content": result.get("response", "No response"),
                    "usage": {"input_tokens": 0, "output_tokens": 0},
                    "stop_reason": "end_turn"
                }
        except Exception as e:
            return self._mock_response(messages)
        return self._mock_response(messages)
    def _mock_response(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        last_message = messages[-1] if messages else {}
        content = last_message.get("content", "")
        if isinstance(content, list):
            content = " ".join([c.get("text", "") for c in content if isinstance(c, dict)])
        responses = [
            f"I understand you're talking about: {content[:100]}...",
            f"Thanks for sharing that. Here's my thoughts on the topic.",
            f"Based on your message, let me provide some insights.",
            f"I've noted your request. This is a mock response since Ollama isn't running."
        ]
        import random
        return {
            "content": random.choice(responses),
            "usage": {"input_tokens": 0, "output_tokens": 0},
            "stop_reason": "end_turn"
        }
ollama_service = OllamaService()