import os

from openai import OpenAI


SYSTEM_PROMPT = "你是一名资深中文职场沟通教练。"


def build_prompt(
    incoming_message: str,
    communication_background: str,
    reference_material: str,
    my_intent: str,
) -> str:
    incoming_text = incoming_message.strip() or "（未提供）"
    return f"""
请基于以下信息生成“一版回复草案”。

要求：
- 仅输出一段可直接发送或轻改后发送的中文回复草案；
- 不编造关键事实；
- 语气专业、清晰、自然；
- 内容尽量覆盖回应、说明、诉求/建议（按输入场景择优）；
- 不要输出多个版本，不要附加解释。

收到的消息：
{incoming_text}

沟通背景：
{communication_background}

参考材料：
{reference_material}

我的意图：
{my_intent}
""".strip()


def generate_reply_with_openai(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 未配置")

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )

    return (response.choices[0].message.content or "").strip()
