from app.database import engine
from app.db_models import User, Workspace, Project, Task, WorkspaceMembership
from sqlmodel import SQLModel
from sqlalchemy import text

if __name__ == "__main__":
    print("Wiping database schema...")
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE;"))
        conn.execute(text("CREATE SCHEMA public;"))
        conn.execute(text("GRANT ALL ON SCHEMA public TO postgres;"))
        conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
        conn.commit()
    
    print("Creating all tables...")
    SQLModel.metadata.create_all(engine)
    print("Reset complete!")
