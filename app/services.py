import os
from pathlib import Path
from typing import Sequence

from openai import OpenAI
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from .models import Matter, ReplyHistory


PROFILE_PATH = Path(__file__).resolve().parent.parent / "data" / "seeds" / "profile.md"


def load_profile_context() -> str:
    if not PROFILE_PATH.exists():
        return "未提供 profile 画像。"
    return PROFILE_PATH.read_text(encoding="utf-8").strip()


def get_memory_context(db: Session, person_id: int, matter_id: int, limit: int = 3) -> str:
    stmt = (
        select(ReplyHistory)
        .where(ReplyHistory.person_id == person_id, ReplyHistory.matter_id == matter_id)
        .order_by(desc(ReplyHistory.created_at))
        .limit(limit)
    )
    recent = db.scalars(stmt).all()

    if not recent:
        return "暂无历史回复记录。"

    lines = ["最近相关沟通记录："]
    for idx, item in enumerate(recent, start=1):
        lines.append(
            f"{idx}. 对方消息：{item.incoming_message[:80]} | 你最终回复：{item.selected_reply[:80]}"
        )
    return "\n".join(lines)


def build_prompt(
    incoming_message: str,
    communication_goal: str,
    matter: Matter,
    memory_context: str,
    profile_context: str,
    modifiers: Sequence[str],
) -> str:
    modifier_text = "、".join(modifiers) if modifiers else "无"
    return f"""
你是一个职场中文沟通副驾。请根据输入生成三种中文回复：
1) 审慎版本（prudent）
2) 简洁版本（concise）
3) 推进版本（push_forward）

要求：
- 不编造事实
- 语气专业、自然
- 与事项背景一致
- 尽量贴合“我的个人沟通画像”
- 输出 JSON，键名严格为 prudent / concise / push_forward

我的个人沟通画像：
{profile_context}

事项标题：{matter.title}
事项详情：{matter.detail or '无'}
历史记忆：{memory_context}

对方消息：{incoming_message}
沟通目标：{communication_goal}
风格调节：{modifier_text}
""".strip()


def generate_replies_with_openai(prompt: str) -> dict[str, str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 未配置")

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        messages=[
            {"role": "system", "content": "你是一名资深中文职场沟通教练。"},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )

    import json

    text = response.choices[0].message.content or "{}"
    payload = json.loads(text)
    return {
        "prudent": payload.get("prudent", ""),
        "concise": payload.get("concise", ""),
        "push_forward": payload.get("push_forward", ""),
    }
