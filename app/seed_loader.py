from pathlib import Path

from sqlalchemy import select

from .database import Base, SessionLocal, engine
from .models import Matter, Person

SEED_DIR = Path(__file__).resolve().parent.parent / "data" / "seeds"


def parse_markdown_blocks(path: Path) -> list[dict[str, str]]:
    """解析“## 小节 + - 字段：值”的 Markdown 模板，兼容中文全角冒号。"""
    blocks: list[dict[str, str]] = []
    current: dict[str, str] = {}

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()

        if line.startswith("## "):
            if current:
                blocks.append(current)
                current = {}
            continue

        if not line.startswith("-"):
            continue

        content = line.lstrip("-").strip()
        if "：" in content:
            key, value = content.split("：", 1)
        elif ":" in content:
            key, value = content.split(":", 1)
        else:
            continue

        current[key.strip()] = value.strip()

    if current:
        blocks.append(current)

    return blocks


def load_people(db):
    blocks = parse_markdown_blocks(SEED_DIR / "people.md")

    for row in blocks:
        name = row.get("姓名", "").strip()
        if not name:
            continue

        exists = db.scalar(select(Person).where(Person.name == name))
        if exists:
            continue

        db.add(
            Person(
                name=name,
                role=row.get("身份/角色", "").strip(),
                relationship_note=(
                    f"与我的关系：{row.get('与我的关系', '').strip()}\n"
                    f"沟通偏好：{row.get('沟通风格偏好', '').strip()}\n"
                    f"注意点：{row.get('需要注意的点', '').strip()}\n"
                    f"备注：{row.get('备注', '').strip()}"
                ).strip(),
            )
        )

    db.commit()

    # 如果模板还没填，给一个默认联系人，确保 MVP 页面可直接操作。
    if not db.scalars(select(Person)).first():
        db.add(Person(name="默认联系人", role="待填写", relationship_note="可在 data/seeds/people.md 修改后重新导入"))
        db.commit()


def load_matters(db):
    blocks = parse_markdown_blocks(SEED_DIR / "matters.md")
    default_person = db.scalars(select(Person).order_by(Person.id)).first()
    default_person_id = default_person.id if default_person else None

    for row in blocks:
        title = row.get("事项名称", "").strip()
        if not title:
            continue

        exists = db.scalar(select(Matter).where(Matter.title == title))
        if exists:
            continue

        detail = (
            f"背景：{row.get('背景', '').strip()}\n"
            f"当前阶段：{row.get('当前阶段', '').strip()}\n"
            f"已形成的共识：{row.get('已形成的共识', '').strip()}\n"
            f"未解决问题：{row.get('还没解决的问题', '').strip()}\n"
            f"下一步动作：{row.get('下一步动作', '').strip()}"
        ).strip()

        db.add(Matter(title=title, detail=detail, person_id=default_person_id))

    db.commit()

    # 如果模板还没填，给一个默认事项，确保 MVP 页面可直接操作。
    if not db.scalars(select(Matter)).first():
        db.add(
            Matter(
                title="默认事项",
                detail="可在 data/seeds/matters.md 修改后重新导入",
                person_id=default_person_id,
            )
        )
        db.commit()


def load_seeds():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        load_people(db)
        load_matters(db)
    finally:
        db.close()


if __name__ == "__main__":
    load_seeds()
    print("Seed data loaded.")
