from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey

from database.base import Base


class Schedule(Base):
    __tablename__ = "schedule"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id"))

    day: Mapped[str] = mapped_column(String)  # Monday, Tuesday...
    subject: Mapped[str] = mapped_column(String)
    time: Mapped[str] = mapped_column(String)
    teacher: Mapped[str] = mapped_column(String, nullable=True)