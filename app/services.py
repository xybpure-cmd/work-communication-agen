def build_mock_reply(
    incoming_message: str,
    communication_background: str,
    reference_material: str,
    my_intent: str,
) -> str:
    """构建 V1.0 原型使用的本地回复草案（不调用模型）。"""

    incoming_text = incoming_message.strip()
    background = communication_background.strip()
    reference = reference_material.strip()
    intent = my_intent.strip()

    context_line = (
        f"收到你的消息，结合当前情况（{background}），"
        if incoming_text
        else f"我这边先同步一下当前情况（{background}），"
    )
    reference_line = f"补充信息是：{reference}，" if reference else ""
    return f"{context_line}{reference_line}{intent}，辛苦你这边看下，如需我补充我会马上同步。"
