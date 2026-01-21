from fastapi import APIRouter, Request, Depends, HTTPException
from typing import List, Optional, Dict, Any, TypeVar, Generic
from app.models.schemas import *
from app.database import get_session
from app.db_models import Workspace
from sqlmodel import Session, select
from pydantic import BaseModel

router = APIRouter(tags=['Workspaces'])

T = TypeVar("T")
class DataWrapper(BaseModel, Generic[T]):
    data: T

class WorkspaceRequestWrapper(BaseModel):
    data: WorkspaceRequest


@router.get("/workspaces", response_model=DataWrapper[List[WorkspaceCompact]] | None, summary="Get multiple workspaces")
async def getworkspaces(request: Request, session: Session = Depends(get_session)):
    workspaces = session.exec(select(Workspace)).all()
    return DataWrapper(data=[WorkspaceCompact(gid=w.gid, resource_type="workspace", name=w.name) for w in workspaces])

@router.post("/workspaces", response_model=DataWrapper[WorkspaceCompact] | None, summary="Create a workspace")
async def createworkspace(body: WorkspaceRequestWrapper, session: Session = Depends(get_session)):
    # WorkspaceRequest is a RootModel -> WorkspaceBase(RootModel) -> WorkspaceCompact
    ws_data = body.data.root.root
    new_ws = Workspace(name=ws_data.name or "Untitled Workspace", resource_type="workspace")
    session.add(new_ws)
    session.commit()
    session.refresh(new_ws)
    return DataWrapper(data=WorkspaceCompact(gid=new_ws.gid, resource_type="workspace", name=new_ws.name))


@router.get("/workspaces/{workspace_gid}", response_model=DataWrapper[WorkspaceCompact] | None, summary="Get a workspace")
async def getworkspace(workspace_gid: str, session: Session = Depends(get_session)):
    workspace = session.get(Workspace, workspace_gid)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return DataWrapper(data=WorkspaceCompact(gid=workspace.gid, resource_type="workspace", name=workspace.name))


@router.put("/workspaces/{workspace_gid}", response_model=dict | None, summary="Update a workspace")
async def updateworkspace(request: Request):
    # Implementation pending
    return {}


@router.post("/workspaces/{workspace_gid}/addUser", response_model=dict | None, summary="Add a user to a workspace or organization")
async def adduserforworkspace(request: Request):
    # Implementation pending
    return {}


@router.post("/workspaces/{workspace_gid}/removeUser", response_model=dict | None, summary="Remove a user from a workspace or organization")
async def removeuserforworkspace(request: Request):
    # Implementation pending
    return {}


@router.get("/workspaces/{workspace_gid}/events", response_model=dict | None, summary="Get workspace events")
async def getworkspaceevents(request: Request):
    # Implementation pending
    return {}

