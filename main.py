from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, field_validator
from database import SessionLocal
from models import Task, TaskLog, User
from typing import Literal
from models import Base
from database import engine

Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

# main.py

class UserCreate(BaseModel):
    name: str
    role: str

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    user_id: int
        
    @field_validator("title")
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError("title cannot be empty")
        return v

class TaskUpdate(BaseModel):
    status: Literal["pending", "in_progress", "done"]

def format_task(t):
    return {
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "status": t.status,
        "user": {
            "id": t.user.id,
            "name": t.user.name
        } if t.user else None,
        "created_at": t.created_at
    }

@app.post("/users")
def create_user(data: UserCreate, db=Depends(get_db)):
    user = User(name=data.name, role=data.role)

    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="db error")

    return user

@app.post("/tasks")
def create_task(data: TaskCreate, db=Depends(get_db)):

    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    task = Task(
        title=data.title,
        description=data.description,
        status="pending",
        user_id=data.user_id
    )

    db.add(task)
    try:
        db.commit()
        db.refresh(task)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="db error")

    return format_task(task)

@app.get("/tasks")
def get_tasks(db = Depends(get_db)):
    tasks = db.query(Task).all()
    return [format_task(t) for t in tasks]

@app.get("/tasks/{task_id}")
def get_task(task_id: int, db = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="task not found")

    return format_task(task)

@app.put("/tasks/{task_id}")
def update_task(task_id: int,  data: TaskUpdate, db = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    
    old_status = task.status
    task.status = data.status

    log = TaskLog(
        task_id=task_id,
        action=f"{old_status} -> {data.status}"
    )
    db.add(log)
    try:
        db.commit()
        db.refresh(task) 
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="db error")
    return format_task(task)

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="task not found")

    db.delete(task)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="db error")
    return {"message": "deleted"}

@app.get("/tasks/{task_id}/logs")
def get_task_logs(task_id: int, db = Depends(get_db)):
    logs = db.query(TaskLog).filter(TaskLog.task_id == task_id).all()
    return logs