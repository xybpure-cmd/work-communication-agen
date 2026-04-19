from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Person(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    role: Mapped[str] = mapped_column(String(120), nullable=True)
    relationship_note: Mapped[str] = mapped_column(Text, nullable=True)

    matters: Mapped[list["Matter"]] = relationship("Matter", back_populates="person")


class Matter(Base):
    __tablename__ = "matters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    detail: Mapped[str] = mapped_column(Text, nullable=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("people.id"), nullable=False)

    person: Mapped[Person] = relationship("Person", back_populates="matters")
    replies: Mapped[list["ReplyHistory"]] = relationship("ReplyHistory", back_populates="matter")


class ReplyHistory(Base):
    __tablename__ = "reply_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("people.id"), nullable=False)
    matter_id: Mapped[int] = mapped_column(ForeignKey("matters.id"), nullable=False)
    incoming_message: Mapped[str] = mapped_column(Text, nullable=False)
    communication_goal: Mapped[str] = mapped_column(Text, nullable=False)
    tone_modifiers: Mapped[str] = mapped_column(String(255), nullable=True)
    generated_prudent: Mapped[str] = mapped_column(Text, nullable=False)
    generated_concise: Mapped[str] = mapped_column(Text, nullable=False)
    generated_push_forward: Mapped[str] = mapped_column(Text, nullable=False)
    selected_reply: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    matter: Mapped[Matter] = relationship("Matter", back_populates="replies")
