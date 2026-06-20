"""Conversation summarization service"""

from app.services.agnes_ai import agnes_ai


SUMMARIZE_PROMPT = (
    "请总结以下客服对话的核心内容，保留关键问题和答案要点，"
    "忽略寒暄用语。输出3-5句话的中文摘要。\n\n"
    "<conversation>\n{history}\n</conversation>"
)


class SummarizeService:
    """对话摘要服务"""

    WINDOW_SIZE = 20  # 保留最近 20 条消息（10 轮对话）
    SUMMARIZE_THRESHOLD = 40  # 超过 40 条消息时触发摘要

    @staticmethod
    async def summarize_early_messages(messages: list) -> str:
        """
        Summarize early messages when context window exceeds threshold.
        messages: list of {"role": "user"/"assistant", "content": "..."}
        Returns summary string, or empty string if no summarization needed.
        """
        if len(messages) <= SummarizeService.WINDOW_SIZE:
            return ""

        # Split: early messages for summarization, recent for sliding window
        early_messages = messages[: -(SummarizeService.WINDOW_SIZE)]

        # Build conversation text for summarization
        history_lines = []
        for msg in early_messages:
            role_label = "用户" if msg["role"] == "user" else "客服"
            history_lines.append(f"{role_label}: {msg['content']}")
        history_text = "\n".join(history_lines)

        prompt = SUMMARIZE_PROMPT.format(history=history_text)
        response = await agnes_ai.chat_completion([
            {"role": "user", "content": prompt},
        ])

        summary = response["choices"][0]["message"]["content"]
        return f"[对话摘要] {summary}\n\n"
