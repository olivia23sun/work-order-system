from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    role = Column(String(20))

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    description = Column(Text)
    status = Column(String(20))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    logs = relationship(
        "TaskLog",
        backref="task",
        cascade="all, delete-orphan"
    )

class TaskLog(Base):
    __tablename__ = "task_logs"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"))
    action = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())

