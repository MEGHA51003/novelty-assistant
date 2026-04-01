import anthropic
from typing import Optional, List, Dict, Any
from app.config import settings


class ClaudeService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"
        self.max_tokens = 4096

    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "read_memory",
                "description": "Read memory entries from the project knowledge base to get relevant context",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "memory_type": {
                            "type": "string",
                            "enum": ["context", "decisions", "todos", "facts", "concepts"],
                            "description": "Type of memory to read. If not specified, reads all types."
                        },
                        "project_id": {
                            "type": "string",
                            "description": "The project ID to read memory from"
                        }
                    },
                    "required": ["project_id"]
                }
            },
            {
                "name": "write_memory",
                "description": "Write a new memory entry to the project knowledge base for persistent storage",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "memory_type": {
                            "type": "string",
                            "enum": ["context", "decisions", "todos", "facts", "concepts"],
                            "description": "Type of memory to create"
                        },
                        "title": {
                            "type": "string",
                            "description": "A brief title for this memory"
                        },
                        "content": {
                            "type": "object",
                            "description": "The memory content as structured data"
                        },
                        "project_id": {
                            "type": "string",
                            "description": "The project ID to write memory to"
                        }
                    },
                    "required": ["memory_type", "title", "content", "project_id"]
                }
            },
            {
                "name": "update_memory",
                "description": "Update an existing memory entry in the project knowledge base",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "memory_id": {
                            "type": "string",
                            "description": "The ID of the memory entry to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "Updated title for the memory"
                        },
                        "content": {
                            "type": "object",
                            "description": "Updated memory content"
                        },
                        "memory_type": {
                            "type": "string",
                            "enum": ["context", "decisions", "todos", "facts", "concepts"],
                            "description": "Updated memory type"
                        }
                    },
                    "required": ["memory_id"]
                }
            },
            {
                "name": "analyze_image",
                "description": "Analyze an image using AI vision to describe its contents or answer questions about it",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "image_url": {
                            "type": "string",
                            "description": "URL of the image to analyze"
                        },
                        "question": {
                            "type": "string",
                            "description": "Specific question or aspect to focus on during analysis"
                        }
                    },
                    "required": ["image_url"]
                }
            }
        ]

    def build_system_prompt(self, project: Dict[str, Any], memory_context: str = "") -> str:
        brief = f"""You are an AI assistant helping with a project.

Project: {project.get('title', 'Untitled')}
Description: {project.get('description', 'No description provided')}
Goals: {project.get('goals', 'No goals specified')}

Reference Links: {', '.join(project.get('reference_links', []) or ['None'])}

Tags: {', '.join(project.get('tags', []) or ['None'])}
"""
        if memory_context:
            brief += f"\n\nRelevant Project Memory:\n{memory_context}"

        brief += """
You have access to tools to:
- Read and write project memory for persistent storage
- Analyze images when users ask about them
- Help organize project information

When users share important information, consider saving key points to memory.
When users ask about images, use the analyze_image tool.
"""
        return brief

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        tools_used: Optional[callable] = None
    ) -> Dict[str, Any]:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=messages,
            tools=self.get_tools()
        )

        result = {
            "content": response.content,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        }

        return result

    def chat_sync(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str
    ) -> Dict[str, Any]:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=messages,
            tools=self.get_tools()
        )

        return {
            "content": response.content,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            },
            "stop_reason": response.stop_reason
        }


claude_service = ClaudeService()
