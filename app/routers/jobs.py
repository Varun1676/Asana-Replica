from fastapi import APIRouter, Request, HTTPException, Depends
from typing import List, Optional, Dict, Any, TypeVar, Generic
from sqlmodel import Session, select
from pydantic import BaseModel
from app.database import get_session
from app.db_models import Job, Project, Task, User
from app.models.schemas import *

router = APIRouter(tags=['Jobs'])

T = TypeVar("T")
class DataWrapper(BaseModel, Generic[T]):
    data: T
    

@router.get("/jobs/{job_gid}", response_model=dict | None, summary="Get a job by id")
async def getjob(job_gid: str, request: Request, session: Session = Depends(get_session)):
    job = session.get(Job, job_gid)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    response_data = {
        "gid": job.gid,
        "resource_type": "job",
        "resource_subtype": job.resource_subtype,
        "status": job.status
    }
    
    if job.new_project_gid:
        project = session.get(Project, job.new_project_gid)
        if project:
            response_data["new_project"] = {
                "gid": project.gid,
                "resource_type": "project",
                "name": project.name
            }
            
    if job.new_task_gid:
        task = session.get(Task, job.new_task_gid)
        if task:
            response_data["new_task"] = {
                 "gid": task.gid,
                 "resource_type": "task",
                 "name": task.name,
                 "resource_subtype": "default_task"
            }
            if job.created_by_gid:
                 response_data["new_task"]["created_by"] = {
                     "gid": job.created_by_gid,
                     "resource_type": "user"
                 }
                 
    return {"data": response_data}

