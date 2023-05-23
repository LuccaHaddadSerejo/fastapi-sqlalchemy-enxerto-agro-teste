from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db_setup import get_db
from schemas.task_schema import TaskCreate, Task, TaskUpdate
from api.utils.task_utils import (
    get_task_by_id,
    get_tasks,
    get_todo_tasks,
    create_task,
    delete_task,
    update_task,
)

router = APIRouter()


@router.get("/tasks", response_model=List[Task], status_code=200)
async def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = get_tasks(db, skip=skip, limit=limit)
    return tasks


@router.get("/tasks/{task_id}", response_model=Task, status_code=200)
async def read_task(task_id: int, db: Session = Depends(get_db)):
    db_task = get_task_by_id(db=db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@router.get("/tasks/list/todo", response_model=List[Task], status_code=200)
async def read_todo_task(db: Session = Depends(get_db)):
    tasks = get_todo_tasks(db=db)
    return tasks


@router.post("/tasks", response_model=Task, status_code=201)
async def create_new_task(task: TaskCreate, db: Session = Depends(get_db)):
    return create_task(db=db, task=task)


@router.patch("/tasks/{task_id}", response_model=Task, status_code=200)
async def update_task_endpoint(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
):
    update_data = task_data.dict(exclude_unset=True)
    return update_task(db=db, task_id=task_id, task_data=update_data)


@router.delete("/tasks/{task_id}", response_model=None, status_code=204)
async def delete_task_endpoint(task_id: int, db: Session = Depends(get_db)):
    db_task = get_task_by_id(db=db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    delete_task(db=db, task_id=task_id)
