"""CampusMate teaching demo REST API (no authentication; local demo only)."""
from contextlib import asynccontextmanager
from datetime import date
import os
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Date, ForeignKey, Integer, String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./campusmate.db")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    course: Mapped[str] = mapped_column(String(80), default="其他")
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    priority: Mapped[str] = mapped_column(String(12), default="medium")
    completed: Mapped[bool] = mapped_column(default=False)

class Expense(Base):
    __tablename__ = "expenses"
    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(30), default="其他")
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    spent_on: Mapped[date] = mapped_column(Date, nullable=False)

class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    course: str = Field(default="其他", max_length=80)
    due_date: date
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")

class TaskOut(TaskIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    completed: bool

class ExpenseIn(BaseModel):
    description: str = Field(min_length=1, max_length=120)
    category: str = Field(default="其他", max_length=30)
    amount: int = Field(gt=0, le=1_000_000)
    spent_on: date

class ExpenseOut(ExpenseIn):
    model_config = ConfigDict(from_attributes=True)
    id: int

class CompleteIn(BaseModel):
    completed: bool

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield

app = FastAPI(title="CampusMate Docker API", version="1.0", lifespan=lifespan)

def get_db():
    with SessionLocal() as db:
        yield db

DB = Annotated[Session, Depends(get_db)]

@app.get("/api/health")
def health(db: DB):
    db.execute(select(func.count()).select_from(Task)).scalar_one()
    return {"status": "ok", "service": "api", "database": "connected"}

@app.get("/api/tasks", response_model=list[TaskOut])
def list_tasks(db: DB):
    return db.scalars(select(Task).order_by(Task.due_date, Task.id)).all()

@app.post("/api/tasks", response_model=TaskOut, status_code=201)
def create_task(data: TaskIn, db: DB):
    item = Task(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@app.patch("/api/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, data: CompleteIn, db: DB):
    item = db.get(Task, task_id)
    if not item:
        raise HTTPException(status_code=404, detail="找不到任務")
    item.completed = data.completed
    db.commit()
    db.refresh(item)
    return item

@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: DB):
    item = db.get(Task, task_id)
    if not item:
        raise HTTPException(status_code=404, detail="找不到任務")
    db.delete(item)
    db.commit()

@app.get("/api/expenses", response_model=list[ExpenseOut])
def list_expenses(db: DB):
    return db.scalars(select(Expense).order_by(Expense.spent_on.desc(), Expense.id.desc())).all()

@app.post("/api/expenses", response_model=ExpenseOut, status_code=201)
def create_expense(data: ExpenseIn, db: DB):
    item = Expense(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@app.delete("/api/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: DB):
    item = db.get(Expense, expense_id)
    if not item:
        raise HTTPException(status_code=404, detail="找不到支出")
    db.delete(item)
    db.commit()

@app.get("/api/stats")
def stats(db: DB):
    tasks = db.scalars(select(Task)).all()
    today = date.today()
    month_start = today.replace(day=1)
    month_total = db.scalar(select(func.coalesce(func.sum(Expense.amount), 0)).where(Expense.spent_on >= month_start, Expense.spent_on <= today))
    return {
        "tasks_total": len(tasks),
        "tasks_pending": sum(not task.completed for task in tasks),
        "tasks_overdue": sum(not task.completed and task.due_date < today for task in tasks),
        "month_expenses": int(month_total),
    }
