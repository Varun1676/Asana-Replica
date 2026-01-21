from fastapi import APIRouter, Request, Depends, HTTPException
from typing import List, Optional, Dict, Any, TypeVar, Generic
from app.models.schemas import *
from app.database import get_session
from app.db_models import Workspace, User, WorkspaceMembership
from sqlmodel import Session, select
from pydantic import BaseModel

router = APIRouter(tags=['Workspaces'])

T = TypeVar("T")
class DataWrapper(BaseModel, Generic[T]):
    data: T

class WorkspaceRequestWrapper(BaseModel):
    data: WorkspaceRequest

class WorkspaceAddUserRequestWrapper(BaseModel):
    data: WorkspaceAddUserRequest

class WorkspaceRemoveUserRequestWrapper(BaseModel):
    data: WorkspaceRemoveUserRequest


from fastapi.responses import JSONResponse

@router.get("/workspaces", response_model=DataWrapper[List[WorkspaceCompact]] | None, summary="Get multiple workspaces")
async def getworkspaces(
    request: Request, 
    limit: int = 20, 
    offset: Optional[str] = None, 
    opt_fields: Optional[List[str]] = None, 
    session: Session = Depends(get_session)
):
    # Basic implementation - ignoring opt_fields implementation for now as it requires dynamic query construction
    # But supporting pagination limit
    if limit < 0:
        limit = 20
        
    workspaces = session.exec(select(Workspace).limit(limit)).all()
    # Asana default response for list is compact
    return DataWrapper(data=[WorkspaceCompact(gid=w.gid, resource_type="workspace", name=w.name) for w in workspaces])

@router.post("/workspaces", response_model=DataWrapper[WorkspaceCompact] | None, summary="Create a workspace")
async def createworkspace(body: WorkspaceRequestWrapper, session: Session = Depends(get_session)):
    # WorkspaceRequest is a RootModel -> WorkspaceBase(RootModel) -> WorkspaceCompact
    # We access the inner data
    ws_data = body.data.root
    while hasattr(ws_data, 'root'):
         ws_data = ws_data.root
         
    new_ws = Workspace(name=ws_data.name or "Untitled Workspace", resource_type="workspace")
    session.add(new_ws)
    session.commit()
    session.refresh(new_ws)
    return DataWrapper(data=WorkspaceCompact(gid=new_ws.gid, resource_type="workspace", name=new_ws.name))


@router.get("/workspaces/{workspace_gid}", response_model=DataWrapper[WorkspaceResponse] | None, summary="Get a workspace")
async def getworkspace(workspace_gid: str, session: Session = Depends(get_session)):
    workspace = session.get(Workspace, workspace_gid)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    return DataWrapper(data=WorkspaceResponse(
        gid=workspace.gid, 
        resource_type="workspace", 
        name=workspace.name,
        email_domains=workspace.email_domains,
        is_organization=workspace.is_organization
    ))


@router.put("/workspaces/{workspace_gid}", response_model=DataWrapper[WorkspaceResponse] | None, summary="Update a workspace")
async def updateworkspace(workspace_gid: str, body: WorkspaceRequestWrapper, session: Session = Depends(get_session)):
    workspace = session.get(Workspace, workspace_gid)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    ws_data = body.data.root
    while hasattr(ws_data, 'root'):
         ws_data = ws_data.root

    if ws_data.name:
        workspace.name = ws_data.name
        
    session.add(workspace)
    session.commit()
    session.refresh(workspace)
    
    return DataWrapper(data=WorkspaceResponse(
        gid=workspace.gid, 
        resource_type="workspace", 
        name=workspace.name,
        email_domains=workspace.email_domains,
        is_organization=workspace.is_organization
    ))

@router.post("/workspaces/{workspace_gid}/addUser", response_model=DataWrapper[UserResponse] | None, summary="Add a user to a workspace or organization")
async def adduserforworkspace(workspace_gid: str, body: WorkspaceAddUserRequestWrapper, session: Session = Depends(get_session)):
    try:
        workspace = session.get(Workspace, workspace_gid)
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        
        user_identifier = body.data.user
        user = None
        
        if user_identifier == "me":
            # Mock 'me' behavior - pick first user or create simple one
            # In a real app, this would come from auth context
            user = session.exec(select(User)).first()
            if not user:
                # Check explicitly for the "me" email to avoid unqiue violation if first() missed it?
                user = session.exec(select(User).where(User.email == "me@example.com")).first()
                if not user:
                    try:
                        user = User(name="Me", email="me@example.com", resource_type="user")
                        session.add(user)
                        session.commit()
                        session.refresh(user)
                    except Exception:
                        session.rollback()
                        user = session.exec(select(User).where(User.email == "me@example.com")).first()
                        if not user:
                             # Should not happen unless other error
                             raise HTTPException(status_code=500, detail="Could not create or find user 'Me'")
        else:
            # Try finding by gid
            user = session.get(User, user_identifier)
            if not user:
                 # Try finding by email
                 user = session.exec(select(User).where(User.email == user_identifier)).first()
                 
        if not user:
             raise HTTPException(status_code=404, detail="User not found")
             
        # Check if membership already exists, if not create it
        membership = session.exec(select(WorkspaceMembership).where(
            WorkspaceMembership.workspace_gid == workspace.gid,
            WorkspaceMembership.user_gid == user.gid
        )).first()
        
        if not membership:
            try:
                membership = WorkspaceMembership(
                    workspace_gid=workspace.gid,
                    user_gid=user.gid,
                    is_active=True
                )
                session.add(membership)
                session.commit()
            except Exception:
                session.rollback()
                # Retry fetch
                membership = session.exec(select(WorkspaceMembership).where(
                    WorkspaceMembership.workspace_gid == workspace.gid,
                    WorkspaceMembership.user_gid == user.gid
                )).first()
            
        # Return the user profile as per specs
        return DataWrapper(data=UserResponse(
            gid=user.gid,
            resource_type="user",
            name=user.name,
            email=user.email,
            photo=None,
            workspaces=[],
            custom_fields=[]
        ))
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"detail": f"DEBUG ERROR: {str(e)}"})


@router.post("/workspaces/{workspace_gid}/removeUser", response_model=DataWrapper[EmptyResponse] | None, summary="Remove a user from a workspace or organization")
async def removeuserforworkspace(workspace_gid: str, body: WorkspaceRemoveUserRequestWrapper, session: Session = Depends(get_session)):
    workspace = session.get(Workspace, workspace_gid)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    user_identifier = body.data.user
    user = None
    
    if user_identifier == "me":
         user = session.exec(select(User)).first()
    else:
        user = session.get(User, user_identifier)
        if not user:
             user = session.exec(select(User).where(User.email == user_identifier)).first()

    if not user:
        # Asana might return 404 or just ignore? Assuming 404 for consistence
        raise HTTPException(status_code=404, detail="User not found")

    membership = session.exec(select(WorkspaceMembership).where(
        WorkspaceMembership.workspace_gid == workspace.gid,
        WorkspaceMembership.user_gid == user.gid
    )).first()
    
    if membership:
        session.delete(membership)
        session.commit()
        
    return DataWrapper(data=EmptyResponse())
