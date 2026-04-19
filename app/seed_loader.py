from pathlib import Path

from sqlalchemy import select

from .database import Base, SessionLocal, engine
from .models import Matter, Person

SEED_DIR = Path(__file__).resolve().parent.parent / "data" / "seeds"


def parse_seed_lines(path: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or not line.startswith("-"):
            continue
        content = line.lstrip("-").strip()
        row: dict[str, str] = {}
        for pair in content.split("|"):
            if ":" not in pair:
                continue
            key, value = pair.split(":", 1)
            row[key.strip()] = value.strip()
        if row:
            entries.append(row)
    return entries


def load_seeds():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        people = parse_seed_lines(SEED_DIR / "people.md")
        for p in people:
            exists = db.scalar(select(Person).where(Person.name == p["name"]))
            if exists:
                continue
            db.add(Person(name=p["name"], role=p.get("role", ""), relationship_note=p.get("note", "")))
        db.commit()

        people_map = {person.name: person.id for person in db.scalars(select(Person)).all()}
        matters = parse_seed_lines(SEED_DIR / "matters.md")
        for m in matters:
            if m.get("person") not in people_map:
                continue
            exists = db.scalar(
                select(Matter).where(Matter.title == m["title"], Matter.person_id == people_map[m["person"]])
            )
            if exists:
                continue
            db.add(
                Matter(
                    title=m["title"],
                    detail=m.get("detail", ""),
                    person_id=people_map[m["person"]],
                )
            )
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    load_seeds()
    print("Seed data loaded.")
