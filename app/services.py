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

    if incoming_text:
        return "\n".join(
            [
                "您好，收到您的消息。",
                "",
                f"结合当前情况：{background}。",
                f"目前可同步的信息是：{reference}。",
                "",
                f"基于以上信息，我这边建议按以下方向推进：{intent}。",
                "如果您认可，我会按这个节奏继续执行，并及时同步最新进展。",
            ]
        )

    return "\n".join(
        [
            "您好，我这边先主动同步一下当前进展。",
            "",
            f"沟通背景：{background}。",
            f"目前关键信息：{reference}。",
            "",
            f"接下来我希望推进的方向是：{intent}。",
            "如您有其他建议，我可以据此调整并尽快落实。",
        ]
    )
