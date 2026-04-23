# models/task.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, Boolean
from sqlalchemy import DateTime
from datetime import datetime
from database.base import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id"))
    title: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(default="pending")
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False)  # Напоминание за день
    reminder_hour_sent: Mapped[bool] = mapped_column(Boolean, default=False)  # Напоминание за час