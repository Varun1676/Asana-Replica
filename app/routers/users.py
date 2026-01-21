from fastapi import APIRouter, Request, Depends, HTTPException
from typing import List, Generic, TypeVar
from app.models.schemas import *
from app.database import get_session
from app.db_models import User
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
