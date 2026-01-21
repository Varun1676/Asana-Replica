from fastapi import APIRouter, Request, Depends, HTTPException
from typing import List, Generic, TypeVar
from app.models.schemas import *
from app.database import get_session
from app.db_models import Project, User, Workspace
from sqlmodel import Session, select
import uuid

router = APIRouter(tags=['Projects'])

T = TypeVar("T")
class DataWrapper(BaseModel, Generic[T]):
    data: T

class ProjectRequestWrapper(BaseModel):
    data: ProjectRequest

@router.get("/projects", response_model=DataWrapper[List[ProjectResponse]] | None, summary="Get multiple projects")
async def getprojects(request: Request, limit: int = 100, session: Session = Depends(get_session)):
    query = select(Project).limit(limit)
    projects = session.exec(query).all()
    
    response_list = []
    for p in projects:
        response_list.append(ProjectResponse(
            gid=p.gid,
            resource_type="project",
            name=p.name,
            workspace=WorkspaceCompact(gid=p.workspace_gid, resource_type="workspace", name="Workspace") if p.workspace_gid else None
        ))
        
    return DataWrapper(data=response_list)

@router.post("/projects", response_model=DataWrapper[ProjectResponse] | None, summary="Create a project")
async def createproject(body: ProjectRequestWrapper, session: Session = Depends(get_session)):
    proj_data = body.data
    
    new_proj = Project(
        name=proj_data.name or "Untitled Project",
        resource_type="project",
        workspace_gid=proj_data.workspace if isinstance(proj_data.workspace, str) else None
    )
    
    session.add(new_proj)
    session.commit()
    session.refresh(new_proj)
    
    return DataWrapper(data=ProjectResponse(
        gid=new_proj.gid,
        resource_type="project",
        name=new_proj.name,
        workspace=WorkspaceCompact(gid=new_proj.workspace_gid, resource_type="workspace", name="Workspace") if new_proj.workspace_gid else None
    ))

@router.get("/projects/{project_gid}", response_model=DataWrapper[ProjectResponse] | None, summary="Get a project")
async def getproject(project_gid: str, session: Session = Depends(get_session)):
    project = session.get(Project, project_gid)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    return DataWrapper(data=ProjectResponse(
        gid=project.gid,
        resource_type="project",
        name=project.name,
        workspace=WorkspaceCompact(gid=project.workspace_gid, resource_type="workspace", name="Workspace") if project.workspace_gid else None
    ))

@router.put("/projects/{project_gid}", response_model=DataWrapper[ProjectResponse] | None, summary="Update a project")
async def updateproject(project_gid: str, body: ProjectRequestWrapper, session: Session = Depends(get_session)):
    project = session.get(Project, project_gid)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = body.data.model_dump(exclude_unset=True)
    if "name" in update_data:
        project.name = update_data["name"]
        
    session.add(project)
    session.commit()
    session.refresh(project)
    
    return DataWrapper(data=ProjectResponse(
        gid=project.gid,
        resource_type="project",
        name=project.name,
        workspace=WorkspaceCompact(gid=project.workspace_gid, resource_type="workspace", name="Workspace") if project.workspace_gid else None
    ))

@router.delete("/projects/{project_gid}", response_model=DataWrapper[dict] | None, summary="Delete a project")
async def deleteproject(project_gid: str, session: Session = Depends(get_session)):
    project = session.get(Project, project_gid)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    session.delete(project)
    session.commit()
    return DataWrapper(data={})
