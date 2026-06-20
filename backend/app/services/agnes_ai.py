"""Agnes AI 多模态模型封装"""

import asyncio
import json
import httpx
from typing import AsyncGenerator, Optional
from app.core.config import settings


class AgnesAI:
    """Agnes AI 多模态模型客户端"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.AGNES_API_KEY
        self.api_base = settings.AGNES_API_BASE
        self.default_model = settings.AGNES_DEFAULT_TEXT_MODEL

    async def _request(self, method: str, path: str, json_data: dict = None):
        """发送 HTTP 请求"""
        async with httpx.AsyncClient(timeout=30) as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            url = f"{self.api_base}{path}"
            resp = await client.request(method, url, json=json_data, headers=headers)
            resp.raise_for_status()
            return resp.json()

    async def chat_completion(
        self,
        messages: list,
        model: Optional[str] = None,
        stream: bool = False,
        max_tokens: int = 2048,
    ) -> dict:
        """文本对话（支持流式）"""
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "max_tokens": max_tokens,
        }
        if stream:
            payload["stream"] = True
        return await self._request("POST", "/chat/completions", payload)

    async def chat_stream(
        self,
        messages: list,
        model: Optional[str] = None,
        stream: bool = False,
        max_tokens: int = 2048,
    ) -> dict:
        """文本对话（支持流式）"""
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "max_tokens": max_tokens,
        }
        if stream:
            payload["stream"] = True
        return await self._request("POST", "/chat/completions", payload)

    async def image_generation(self, prompt: str, size: str = "1024x1024") -> dict:
        """图片生成"""
        return await self._request(
            "POST",
            "/images/generations",
            {"model": "agnes-image-2.1-flash", "prompt": prompt, "size": size},
        )

    async def video_create(self, prompt: str, width: int = 1152, height: int = 768) -> dict:
        """视频生成（异步任务）"""
        return await self._request(
            "POST",
            "/videos",
            {
                "model": "agnes-video-v2.0",
                "prompt": prompt,
                "width": width,
                "height": height,
                "num_frames": 121,
                "frame_rate": 24,
            },
        )

    async def image_recognition(self, image_url: str, question: str = "请描述这张图片的内容") -> dict:
        """图片识别"""
        return await self._request(
            "POST",
            "/chat/completions",
            {
                "model": "agnes-2.0-flash",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": question},
                            {"type": "image_url", "image_url": {"url": image_url, "detail": "high"}},
                        ],
                    }
                ],
                "max_tokens": 2048,
            },
        )

    async def embedding(self, text: str, model: str = "agnes-embedding-v1") -> dict:
        """Generate embedding vector for text. Returns OpenAI-compatible dict."""
        payload = {
            "model": model,
            "input": text,
        }
        return await self._request("POST", "/embeddings", payload)


# 单例
agnes_ai = AgnesAI()
