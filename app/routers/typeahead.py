from fastapi import APIRouter, Request, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, col
from app.database import get_session
from app.db_models import User, Task, Project, Workspace, WorkspaceMembership
from app.models.schemas import *

router = APIRouter(tags=['Typeahead'])


@router.get("/workspaces/{workspace_gid}/typeahead", response_model=dict | None, summary="Get objects via typeahead")
async def typeaheadforworkspace(
    workspace_gid: str,
    request: Request,
    resource_type: str = "user", # Defaulting to user as common case, but normally required
    type: Optional[str] = None, # Deprecated alias for resource_type
    query: Optional[str] = None,
    count: int = 20,
    session: Session = Depends(get_session)
):
    # Asana logic: type is alias for resource_type if provided
    target_type = type if type else resource_type
    
    results = []
    
    # Check if workspace exists
    workspace = session.get(Workspace, workspace_gid)
    if not workspace:
         raise HTTPException(status_code=404, detail="Workspace not found")

    if target_type == "user":
        # Join User and WorkspaceMembership to find users in this workspace
        statement = select(User).join(WorkspaceMembership).where(
            WorkspaceMembership.workspace_gid == workspace_gid,
            WorkspaceMembership.user_gid == User.gid
        )
        if query:
            statement = statement.where(col(User.name).contains(query))
            
        users = session.exec(statement.limit(count)).all()
        for u in users:
            results.append({
                "gid": u.gid,
                "resource_type": "user",
                "name": u.name
            })

    elif target_type == "task":
        statement = select(Task).where(Task.workspace_gid == workspace_gid)
        if query:
            statement = statement.where(col(Task.name).contains(query))
            
        tasks = session.exec(statement.limit(count)).all()
        for t in tasks:
            results.append({
                "gid": t.gid,
                "resource_type": "task",
                "name": t.name
            })
            
    elif target_type == "project":
        statement = select(Project).where(Project.workspace_gid == workspace_gid)
        if query:
            statement = statement.where(col(Project.name).contains(query))
            
        projects = session.exec(statement.limit(count)).all()
        for p in projects:
            results.append({
                "gid": p.gid,
                "resource_type": "project",
                "name": p.name
            })
    
    # Handle other types or return empty if unsupported
    
    return {"data": results}

