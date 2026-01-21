from fastapi import APIRouter, Request, Depends, HTTPException
from typing import List, Optional, Dict, Any, TypeVar, Generic
from sqlmodel import Session, select
from pydantic import BaseModel
from app.database import get_session
from app.db_models import ProjectBrief, Project
from app.models.schemas import *

router = APIRouter(tags=['Project briefs'])

T = TypeVar("T")
class DataWrapper(BaseModel, Generic[T]):
    data: T

class ProjectBriefRequestWrapper(BaseModel):
    data: ProjectBriefRequest

@router.get("/project_briefs/{project_brief_gid}", response_model=DataWrapper[ProjectBriefResponse] | None, summary="Get a project brief")
async def getprojectbrief(project_brief_gid: str, request: Request, session: Session = Depends(get_session)):
    brief = session.get(ProjectBrief, project_brief_gid)
    if not brief:
        raise HTTPException(status_code=404, detail="Project Brief not found")
        
    project = session.get(Project, brief.project_gid)
    
    return DataWrapper(
        data=ProjectBriefResponse(
            gid=brief.gid,
            resource_type="project_brief",
            title=brief.title,
            html_text=brief.html_text,
            text=brief.text,
            permalink_url=f"https://app.asana.com/0/{brief.project_gid}/{brief.gid}",
            project=ProjectCompact(gid=project.gid, resource_type="project", name=project.name) if project else None
        )
    )


@router.put("/project_briefs/{project_brief_gid}", response_model=DataWrapper[ProjectBriefResponse] | None, summary="Update a project brief")
async def updateprojectbrief(project_brief_gid: str, body: ProjectBriefRequestWrapper, session: Session = Depends(get_session)):
    brief = session.get(ProjectBrief, project_brief_gid)
    if not brief:
        raise HTTPException(status_code=404, detail="Project Brief not found")
        
    data = body.data
    changed = False
    
    if data.title is not None:
        brief.title = data.title
        changed = True
    if data.html_text is not None:
        brief.html_text = data.html_text
        changed = True
    if data.text is not None:
        brief.text = data.text
        changed = True
        
    if changed:
        session.add(brief)
        session.commit()
        session.refresh(brief)
        
    project = session.get(Project, brief.project_gid)
    
    return DataWrapper(
        data=ProjectBriefResponse(
            gid=brief.gid,
            resource_type="project_brief",
            title=brief.title,
            html_text=brief.html_text,
            text=brief.text,
            permalink_url=f"https://app.asana.com/0/{brief.project_gid}/{brief.gid}",
            project=ProjectCompact(gid=project.gid, resource_type="project", name=project.name) if project else None
        )
    )


@router.delete("/project_briefs/{project_brief_gid}", response_model=DataWrapper[EmptyResponse] | None, summary="Delete a project brief")
async def deleteprojectbrief(project_brief_gid: str, request: Request, session: Session = Depends(get_session)):
    brief = session.get(ProjectBrief, project_brief_gid)
    if not brief:
        raise HTTPException(status_code=404, detail="Project Brief not found")
        
    session.delete(brief)
    session.commit()
    
    return DataWrapper(data=EmptyResponse())


@router.post("/projects/{project_gid}/project_briefs", response_model=DataWrapper[ProjectBriefResponse] | None, summary="Create a project brief")
async def createprojectbrief(project_gid: str, body: ProjectBriefRequestWrapper, session: Session = Depends(get_session)):
    project = session.get(Project, project_gid)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    data = body.data
    
    new_brief = ProjectBrief(
        project_gid=project.gid,
        resource_type="project_brief",
        title=data.title or f"{project.name} - Project Brief", # Default title if missing?
        html_text=data.html_text,
        text=data.text
    )
    
    session.add(new_brief)
    session.commit()
    session.refresh(new_brief)
    
    return DataWrapper(
        data=ProjectBriefResponse(
            gid=new_brief.gid,
            resource_type="project_brief",
            title=new_brief.title,
            html_text=new_brief.html_text,
            text=new_brief.text,
            permalink_url=f"https://app.asana.com/0/{new_brief.project_gid}/{new_brief.gid}",
            project=ProjectCompact(gid=project.gid, resource_type="project", name=project.name)
        )
    )
