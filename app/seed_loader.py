from pathlib import Path

from sqlalchemy import select

from .database import Base, SessionLocal, engine
from .models import Matter, Person

SEED_DIR = Path(__file__).resolve().parent.parent / "data" / "seeds"

PEOPLE_KEY_MAP = {
    "姓名": "name",
    "身份/角色": "role",
    "与我的关系": "relationship_note",
    "沟通风格偏好": "communication_style",
    "需要注意的点": "attention_points",
    "备注": "note",
}

MATTER_KEY_MAP = {
    "事项名称": "title",
    "背景": "background",
    "当前阶段": "stage",
    "已形成的共识": "consensus",
    "还没解决的问题": "open_issues",
    "下一步动作": "next_action",
}


def parse_markdown_sections(path: Path) -> list[dict[str, str]]:
    sections: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()

        if line.startswith("## "):
            if current:
                sections.append(current)
            current = {}
            continue

        if not current or not line.startswith("-") or "：" not in line:
            continue

        content = line.lstrip("-").strip()
        key, value = content.split("：", 1)
        current[key.strip()] = value.strip()

    if current:
        sections.append(current)

    return sections


def join_person_note(item: dict[str, str]) -> str:
    parts = []
    if item.get("与我的关系"):
        parts.append(f"与我的关系：{item['与我的关系']}")
    if item.get("沟通风格偏好"):
        parts.append(f"沟通风格偏好：{item['沟通风格偏好']}")
    if item.get("需要注意的点"):
        parts.append(f"需要注意的点：{item['需要注意的点']}")
    if item.get("备注"):
        parts.append(f"备注：{item['备注']}")
    return "；".join(parts)


def join_matter_detail(item: dict[str, str]) -> str:
    parts = []
    if item.get("背景"):
        parts.append(f"背景：{item['背景']}")
    if item.get("当前阶段"):
        parts.append(f"当前阶段：{item['当前阶段']}")
    if item.get("已形成的共识"):
        parts.append(f"已形成的共识：{item['已形成的共识']}")
    if item.get("还没解决的问题"):
        parts.append(f"还没解决的问题：{item['还没解决的问题']}")
    if item.get("下一步动作"):
        parts.append(f"下一步动作：{item['下一步动作']}")
    return "；".join(parts)


def is_placeholder(value: str | None) -> bool:
    if not value:
        return True
    v = value.strip()
    return v in {"", "请填写姓名", "请填写事项名称"}


def load_seeds():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        people_sections = parse_markdown_sections(SEED_DIR / "people.md")
        for item in people_sections:
            name = item.get("姓名", "").strip()
            if is_placeholder(name):
                continue

            exists = db.scalar(select(Person).where(Person.name == name))
            if exists:
                exists.role = item.get("身份/角色", exists.role)
                exists.relationship_note = join_person_note(item)
                continue

            db.add(
                Person(
                    name=name,
                    role=item.get("身份/角色", ""),
                    relationship_note=join_person_note(item),
                )
            )
        db.commit()

        people_map = {person.name: person.id for person in db.scalars(select(Person)).all()}
        matter_sections = parse_markdown_sections(SEED_DIR / "matters.md")
        for item in matter_sections:
            title = item.get("事项名称", "").strip()
            if is_placeholder(title):
                continue

            # 简化策略：优先把事项关联到第一个人物；如需更细粒度可在模板中后续增加“关联人物”。
            if not people_map:
                continue
            fallback_person_id = next(iter(people_map.values()))

            exists = db.scalar(select(Matter).where(Matter.title == title))
            detail_text = join_matter_detail(item)
            if exists:
                exists.detail = detail_text
                continue

            db.add(Matter(title=title, detail=detail_text, person_id=fallback_person_id))
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    load_seeds()
    print("Seed data loaded.")
