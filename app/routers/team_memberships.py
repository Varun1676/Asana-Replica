from fastapi import APIRouter, Request, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any, TypeVar, Generic
from sqlmodel import Session, select
from pydantic import BaseModel
from app.database import get_session
from app.db_models import TeamMembership, User, Team
from app.models.schemas import *

router = APIRouter(tags=['Team memberships'])

T = TypeVar("T")
class DataWrapper(BaseModel, Generic[T]):
    data: T

def _construct_team_membership_response(mem: TeamMembership, session: Session) -> TeamMembershipCompact:
    # Fetch related
    user = session.get(User, mem.user_gid)
    team = session.get(Team, mem.team_gid)
    
    return TeamMembershipCompact(
        gid=mem.gid,
        resource_type="team_membership",
        user=UserCompact(gid=user.gid, resource_type="user", name=user.name) if user else None,
        team=TeamCompact(gid=team.gid, resource_type="team", name=team.name) if team else None,
        is_guest=mem.is_guest,
        is_admin=mem.is_admin,
        is_limited_access=False # Default
    )

@router.get("/team_memberships/{team_membership_gid}", response_model=DataWrapper[TeamMembershipCompact] | None, summary="Get a team membership")
async def getteammembership(team_membership_gid: str, request: Request, session: Session = Depends(get_session)):
    mem = session.get(TeamMembership, team_membership_gid)
    if not mem:
        raise HTTPException(status_code=404, detail="Team membership not found")
        
    return DataWrapper(data=_construct_team_membership_response(mem, session))


@router.get("/team_memberships", response_model=DataWrapper[List[TeamMembershipCompact]] | None, summary="Get team memberships")
async def getteammemberships(
    request: Request,
    team: Optional[str] = Query(None),
    user: Optional[str] = Query(None),
    workspace: Optional[str] = Query(None),
    limit: int = 20,
    session: Session = Depends(get_session)
):
    query = select(TeamMembership).limit(limit)
    
    if team:
        query = query.where(TeamMembership.team_gid == team)
    if user:
        query = query.where(TeamMembership.user_gid == user)
    # Workspace filter might require joining team if workspace_gid not on membership explicitly
    # But currently TeamMembership HAS workspace_gid (added in previous edit? Yes).
    if workspace:
        query = query.where(TeamMembership.workspace_gid == workspace)
        
    mems = session.exec(query).all()
    results = [_construct_team_membership_response(m, session) for m in mems]
    return DataWrapper(data=results)


@router.get("/teams/{team_gid}/team_memberships", response_model=DataWrapper[List[TeamMembershipCompact]] | None, summary="Get memberships from a team")
async def getteammembershipsforteam(team_gid: str, request: Request, session: Session = Depends(get_session)):
    team = session.get(Team, team_gid)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
        
    mems = session.exec(select(TeamMembership).where(TeamMembership.team_gid == team_gid)).all()
    results = [_construct_team_membership_response(m, session) for m in mems]
    return DataWrapper(data=results)


@router.get("/users/{user_gid}/team_memberships", response_model=DataWrapper[List[TeamMembershipCompact]] | None, summary="Get memberships from a user")
async def getteammembershipsforuser(user_gid: str, request: Request, session: Session = Depends(get_session)):
    # Verify user?
    # Asana often allows listing for valid user gid even if caller is diff (depends on permissions)
    # We'll just query.
    
    mems = session.exec(select(TeamMembership).where(TeamMembership.user_gid == user_gid)).all()
    results = [_construct_team_membership_response(m, session) for m in mems]
    return DataWrapper(data=results)

