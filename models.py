from sqlalchemy import Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from sqlalchemy import Integer, BigInteger, String, DateTime, ForeignKey

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)  # ✅ Заменили на BigInteger
    name: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    location: Mapped[str] = mapped_column(String, nullable=True)
    salary: Mapped[str] = mapped_column(String, nullable=True)
    work_time: Mapped[str] = mapped_column(String, nullable=True)
    contact: Mapped[str] = mapped_column(String, nullable=True)  # ✅ Осталось
    employer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    employer: Mapped["User"] = relationship("User")

class Request(Base):
    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id"))
    seeker_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String, default="pending")  # pending, accepted, rejected
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    seeker: Mapped["User"] = relationship("User", foreign_keys=[seeker_id])
    job: Mapped["Job"] = relationship("Job")