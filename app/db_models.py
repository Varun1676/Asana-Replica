from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import JSON
from datetime import datetime
import uuid

# 1. The Base Model
class BaseDBModel(SQLModel):
    gid: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    resource_type: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # FIX: Use sa_type=JSON instead of sa_column=Column(JSON)
    # This ensures a new column is created for every inheriting table
    meta_data: Dict[str, Any] = Field(default={}, sa_type=JSON)

# 2. Users Table
class User(BaseDBModel, table=True):
    name: str
    email: str = Field(unique=True, index=True)
    
    # Relationships
    tasks: List["Task"] = Relationship(back_populates="assignee")

# 3. Workspaces Table
class Workspace(BaseDBModel, table=True):
    name: str
    email_domains: List[str] = Field(default=[], sa_type=JSON)
    is_organization: bool = Field(default=False)
    
    projects: List["Project"] = Relationship(back_populates="workspace")
    tasks: List["Task"] = Relationship(back_populates="workspace")

# 4. Projects Table
class Project(BaseDBModel, table=True):
    name: str
    workspace_gid: Optional[str] = Field(default=None, foreign_key="workspace.gid")
    
    # Relationships
    workspace: Optional[Workspace] = Relationship(back_populates="projects")
    tasks: List["Task"] = Relationship(back_populates="project")
    project_briefs: List["ProjectBrief"] = Relationship(back_populates="project")

# 5. Project Briefs
class ProjectBrief(BaseDBModel, table=True):
    title: Optional[str] = None
    html_text: Optional[str] = None
    text: Optional[str] = None
    project_gid: str = Field(foreign_key="project.gid")
    
    project: Optional[Project] = Relationship(back_populates="project_briefs")

# 6. Tasks Table
class Task(BaseDBModel, table=True):
    name: str
    completed: bool = False
    notes: Optional[str] = None
    
    # Foreign Keys
    assignee_gid: Optional[str] = Field(default=None, foreign_key="user.gid")
    workspace_gid: Optional[str] = Field(default=None, foreign_key="workspace.gid")
    project_gid: Optional[str] = Field(default=None, foreign_key="project.gid")

    # Relationships
    assignee: Optional[User] = Relationship(back_populates="tasks")
    workspace: Optional[Workspace] = Relationship(back_populates="tasks")
    project: Optional[Project] = Relationship(back_populates="tasks")

# 8. Teams
class Team(BaseDBModel, table=True):
    name: str
    description: Optional[str] = None
    workspace_gid: str = Field(foreign_key="workspace.gid")
    visibility: str = "public"
    
    workspace: Optional[Workspace] = Relationship()

# 9. Team Memberships
class TeamMembership(BaseDBModel, table=True):
    team_gid: str = Field(foreign_key="team.gid")
    user_gid: str = Field(foreign_key="user.gid")
    is_admin: bool = False
    is_guest: bool = False
    workspace_gid: Optional[str] = Field(default=None, foreign_key="workspace.gid")
    project_gid: Optional[str] = Field(default=None, foreign_key="project.gid")

# 6. Workspace Memberships
class WorkspaceMembership(BaseDBModel, table=True):
    user_gid: str = Field(foreign_key="user.gid")
    workspace_gid: str = Field(foreign_key="workspace.gid")
    is_active: bool = True
    is_admin: bool = False
    is_guest: bool = False

# 7. Jobs
class Job(BaseDBModel, table=True):
    resource_subtype: Optional[str] = None
    status: str = "in_progress"
    new_project_gid: str = Field(foreign_key="project.gid")
    new_task_gid: str = Field(foreign_key="task.gid")
    created_by_gid: Optional[str] = Field(default=None, foreign_key="user.gid")
