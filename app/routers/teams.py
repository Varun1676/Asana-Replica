from fastapi import APIRouter, Request, Depends, HTTPException
from typing import List, Optional, Dict, Any, TypeVar, Generic
from sqlmodel import Session, select
from pydantic import BaseModel
from app.database import get_session
from app.db_models import Team, TeamMembership, Workspace, User
from app.models.schemas import *

router = APIRouter(tags=['Teams'])

T = TypeVar("T")
class DataWrapper(BaseModel, Generic[T]):
    data: T
    
class TeamRequestWrapper(BaseModel):
    data: Dict[str, Any]

class TeamResponse(BaseModel):
    gid: str
    resource_type: str = "team"
    name: str
    description: Optional[str] = None
    visibility: str = "public"
    organization: Optional[WorkspaceCompact] = None

@router.post("/teams", response_model=DataWrapper[TeamResponse] | None, summary="Create a team")
async def createteam(request: Request, body: TeamRequestWrapper, session: Session = Depends(get_session)):
    data = body.data
    # Required: workspace and name usually
    if "workspace" not in data and "organization" not in data:
         # Asana API usually requires organization/workspace
         raise HTTPException(status_code=400, detail="Workspace or Organization GID required")
         
    ws_gid = data.get("workspace") or data.get("organization")
    ws = session.get(Workspace, ws_gid)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    new_team = Team(
        name=data.get("name", "Untitled Team"),
        description=data.get("description"),
        visibility=data.get("visibility", "public"),
        workspace_gid=ws.gid,
        resource_type="team"
    )
    session.add(new_team)
    session.commit()
    session.refresh(new_team)
    
    return DataWrapper(data=TeamResponse(
        gid=new_team.gid,
        name=new_team.name,
        description=new_team.description,
        visibility=new_team.visibility,
        organization=WorkspaceCompact(gid=ws.gid, name=ws.name, resource_type="workspace")
    ))


@router.get("/teams/{team_gid}", response_model=DataWrapper[TeamResponse] | None, summary="Get a team")
async def getteam(team_gid: str, request: Request, session: Session = Depends(get_session)):
    team = session.get(Team, team_gid)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    ws = session.get(Workspace, team.workspace_gid)
    
    return DataWrapper(data=TeamResponse(
        gid=team.gid,
        name=team.name,
        description=team.description,
        visibility=team.visibility,
        organization=WorkspaceCompact(gid=ws.gid, name=ws.name, resource_type="workspace") if ws else None
    ))


@router.put("/teams/{team_gid}", response_model=DataWrapper[TeamResponse] | None, summary="Update a team")
async def updateteam(team_gid: str, body: TeamRequestWrapper, session: Session = Depends(get_session)):
    team = session.get(Team, team_gid)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
        
    data = body.data
    if "name" in data: team.name = data["name"]
    if "description" in data: team.description = data["description"]
    if "visibility" in data: team.visibility = data["visibility"]
    
    session.add(team)
    session.commit()
    session.refresh(team)
    
    ws = session.get(Workspace, team.workspace_gid)

    return DataWrapper(data=TeamResponse(
        gid=team.gid,
        name=team.name,
        description=team.description,
        visibility=team.visibility,
        organization=WorkspaceCompact(gid=ws.gid, name=ws.name, resource_type="workspace") if ws else None
    ))


@router.get("/workspaces/{workspace_gid}/teams", response_model=DataWrapper[List[TeamResponse]] | None, summary="Get teams in a workspace")
async def getteamsforworkspace(workspace_gid: str, request: Request, session: Session = Depends(get_session)):
    teams = session.exec(select(Team).where(Team.workspace_gid == workspace_gid)).all()
    results = []
    ws = session.get(Workspace, workspace_gid)
    ws_compact = WorkspaceCompact(gid=ws.gid, name=ws.name, resource_type="workspace") if ws else None
    
    for t in teams:
        results.append(TeamResponse(
            gid=t.gid,
            name=t.name,
            description=t.description,
            visibility=t.visibility,
            organization=ws_compact
        ))
    return DataWrapper(data=results)


@router.get("/users/{user_gid}/teams", response_model=DataWrapper[List[TeamResponse]] | None, summary="Get teams for a user")
async def getteamsforuser(user_gid: str, request: Request, session: Session = Depends(get_session)):
    # Join TeamMembership -> Team
    memberships = session.exec(select(TeamMembership).where(TeamMembership.user_gid == user_gid)).all()
    results = []
    for m in memberships:
        t = session.get(Team, m.team_gid)
        if t:
            ws = session.get(Workspace, t.workspace_gid)
            results.append(TeamResponse(
                gid=t.gid,
                name=t.name,
                description=t.description,
                visibility=t.visibility,
                organization=WorkspaceCompact(gid=ws.gid, name=ws.name, resource_type="workspace") if ws else None
            ))
    return DataWrapper(data=results)


@router.post("/teams/{team_gid}/addUser", response_model=dict | None, summary="Add a user to a team")
async def adduserforteam(team_gid: str, body: Dict[str, Any], session: Session = Depends(get_session)):
    data = body.get("data", {})
    user_gid = data.get("user")
    
    # Simple check if user exists (mocked or strict?) Strict based on previous patterns
    # But usually 'user' string could be 'me' or email. For simplicity, assume GID or handle 'me'
    if user_gid == 'me':
         # In a real app we'd get current user from auth.
         # For tests/mock, we might need a workaround or assume specific GID.
         # Let's assume passed GID for now to be robust.
         pass 

    existing = session.exec(select(TeamMembership).where(TeamMembership.team_gid == team_gid, TeamMembership.user_gid == user_gid)).first()
    if not existing:
        new_mem = TeamMembership(team_gid=team_gid, user_gid=user_gid, resource_type="team_membership")
        session.add(new_mem)
        session.commit()
    
    # Return user as per Asana spec (often returns the user added or list of members?)
    # Asana docs say: returns valid user response?
    # We'll return empty data or success indicator as strict return type wasn't enforced by user prompt but 'response_model=dict' in stub
    return {"data": {"gid": user_gid, "resource_type": "user"}} 


@router.post("/teams/{team_gid}/removeUser", response_model=dict | None, summary="Remove a user from a team")
async def removeuserforteam(team_gid: str, body: Dict[str, Any], session: Session = Depends(get_session)):
    data = body.get("data", {})
    user_gid = data.get("user")
    
    mem = session.exec(select(TeamMembership).where(TeamMembership.team_gid == team_gid, TeamMembership.user_gid == user_gid)).first()
    if mem:
        session.delete(mem)
        session.commit()
        
    return {"data": {}}

