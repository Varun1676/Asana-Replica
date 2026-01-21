from fastapi import APIRouter, Request, Depends, HTTPException
from typing import List, Generic, TypeVar
from app.models.schemas import *
from app.database import get_session
from app.db_models import User, Workspace, WorkspaceMembership
from sqlmodel import Session, select
import uuid

router = APIRouter(tags=['Users'])

T = TypeVar("T")
class DataWrapper(BaseModel, Generic[T]):
    data: T

# Note: User creation often handled differently in Asana (workspace invites), but accessible via admin API
# We'll treat it as standard resource for replica

# Can't find UserRequest easily, use UserBase or manual
class UserRequestWrapper(BaseModel):
    data: dict 

@router.get("/users", response_model=DataWrapper[List[UserResponse]] | None, summary="Get multiple users")
async def getusers(request: Request, limit: int = 100, session: Session = Depends(get_session)):
    query = select(User).limit(limit)
    users = session.exec(query).all()
    
    response_list = []
    for u in users:
        response_list.append(UserResponse(
            gid=u.gid,
            resource_type="user",
            name=u.name,
            email=u.email
        ))
        
    return DataWrapper(data=response_list)

@router.get("/users/{user_gid}", response_model=DataWrapper[UserResponse] | None, summary="Get a user")
async def getuser(user_gid: str, session: Session = Depends(get_session)):
    # Handle "me" alias
    if user_gid == "me":
        # Return first user or mock
        user = session.exec(select(User)).first()
        if not user:
             # Auto-create if not exists for demo
             user = User(name="Demo User", email="me@example.com", resource_type="user")
             session.add(user)
             session.commit()
             session.refresh(user)
    else:
        user = session.get(User, user_gid)
        
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return DataWrapper(data=UserResponse(
        gid=user.gid,
        resource_type="user",
        name=user.name,
        email=user.email
    ))

@router.put("/users/{user_gid}", response_model=DataWrapper[UserResponse] | None, summary="Update a user")
async def updateuser(user_gid: str, body: UserRequestWrapper, session: Session = Depends(get_session)):
    user = session.get(User, user_gid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user_data = body.data
    
    # Init meta_data if None
    if user.meta_data is None:
        user.meta_data = {}
    
    changed = False
    
    if "name" in user_data:
        user.name = user_data["name"]
        changed = True
        
    if "custom_fields" in user_data:
        # Pydantic JSON field update pattern
        current_meta = dict(user.meta_data) if user.meta_data else {}
        if "custom_fields" not in current_meta:
            current_meta["custom_fields"] = {}
        
        current_meta["custom_fields"].update(user_data["custom_fields"])
        user.meta_data = current_meta
        changed = True

    if changed:
        session.add(user)
        session.commit()
        session.refresh(user)
    
    # 1. Workspaces (via DB relationships)
    memberships = session.exec(select(WorkspaceMembership).where(WorkspaceMembership.user_gid == user.gid)).all()
    workspaces_list = []
    for m in memberships:
        ws = session.get(Workspace, m.workspace_gid)
        if ws:
            workspaces_list.append(WorkspaceCompact(gid=ws.gid, resource_type="workspace", name=ws.name))

    # 2. Custom Fields (via DB metadata)
    custom_fields_response = []
    stored_cfs = user.meta_data.get("custom_fields", {})
    if stored_cfs:
        for key, val in stored_cfs.items():
            # Construct a compact representation from the stored key-value
            # We don't have full CustomField definitions in DB, so we emulate the structure based on stored data
            custom_fields_response.append(CustomFieldCompact(
                gid=None, # No actual GID for these ad-hoc fields
                resource_type="custom_field",
                name=key,
                text_value=str(val),
                type="text", # Default assumption
                enabled=True
            ))

    return DataWrapper(data=UserResponse(
        gid=user.gid,
        resource_type="user",
        name=user.name,
        email=user.email,
        # photo is not in DB, so we omit/return None to avoid generic mocks
        photo=None,
        workspaces=workspaces_list,
        custom_fields=custom_fields_response
    ))