from fastapi import APIRouter, Request, Depends, HTTPException
from typing import List, Optional, Dict, Any, Generic, TypeVar
from app.models.schemas import *
from app.database import get_session
from app.db_models import Task, User, Project, Workspace
from sqlmodel import Session, select
import uuid

router = APIRouter(tags=['Tasks'])

T = TypeVar("T")
class DataWrapper(BaseModel, Generic[T]):
    data: T

# We need a wrapper for input that matches { "data": TaskRequest }
class TaskRequestWrapper(BaseModel):
    data: TaskRequest

@router.get("/tasks", response_model=DataWrapper[List[TaskResponse]] | None, summary="Get multiple tasks")
async def gettasks(request: Request, limit: int = 100, offset: str = None, session: Session = Depends(get_session)):
    query = select(Task).limit(limit)
    tasks = session.exec(query).all()
    
    # Simple conversion
    response_tasks = []
    for t in tasks:
        # We construct TaskResponse. Note: schemas.py TaskResponse has many fields.
        # We only populate what we have.
        response_tasks.append(
            TaskResponse(
                gid=t.gid,
                resource_type="task",
                name=t.name,
                notes=t.notes,
                completed=t.completed
            )
        )
        
    return DataWrapper(data=response_tasks)


@router.post("/tasks", response_model=DataWrapper[TaskResponse] | None, summary="Create a task")
async def createtask(body: TaskRequestWrapper, session: Session = Depends(get_session)):
    task_data = body.data
    
    # Map Pydantic to SQLModel
    # Note: TaskRequest fields might be None, handled by default
    new_task = Task(
        name=task_data.name or "Untitled Task",
        notes=task_data.notes,
        completed=task_data.completed or False,
        resource_type="task",
        assignee_gid=task_data.assignee if isinstance(task_data.assignee, str) else None, # Assignee might be dict in some contexts? Spec says str for input usually
        workspace_gid=task_data.workspace if isinstance(task_data.workspace, str) else None
    )
    
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    
    return DataWrapper(data=TaskResponse(
        gid=new_task.gid,
        resource_type="task",
        name=new_task.name,
        notes=new_task.notes,
        completed=new_task.completed
    ))


@router.get("/tasks/{task_gid}", response_model=DataWrapper[TaskResponse] | None, summary="Get a task")
async def gettask(task_gid: str, session: Session = Depends(get_session)):
    task = session.get(Task, task_gid)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return DataWrapper(data=TaskResponse(
        gid=task.gid,
        resource_type="task",
        name=task.name,
        notes=task.notes,
        completed=task.completed
    ))


@router.put("/tasks/{task_gid}", response_model=DataWrapper[TaskResponse] | None, summary="Update a task")
async def updatetask(task_gid: str, body: TaskRequestWrapper, session: Session = Depends(get_session)):
    task = session.get(Task, task_gid)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    update_data = body.data.model_dump(exclude_unset=True)
    
    if "name" in update_data:
        task.name = update_data["name"]
    if "notes" in update_data:
        task.notes = update_data["notes"]
    if "completed" in update_data:
        task.completed = update_data["completed"]
        
    session.add(task)
    session.commit()
    session.refresh(task)
        
    return DataWrapper(data=TaskResponse(
        gid=task.gid,
        resource_type="task",
        name=task.name,
        notes=task.notes,
        completed=task.completed
    ))

@router.delete("/tasks/{task_gid}", response_model=DataWrapper[dict] | None, summary="Delete a task")
async def deletetask(task_gid: str, session: Session = Depends(get_session)):
    task = session.get(Task, task_gid)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    session.delete(task)
    session.commit()
    return DataWrapper(data={})

# ... other endpoints (kept generic or pending) ...
