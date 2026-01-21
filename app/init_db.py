from app.database import create_db_and_tables
# Import models so SQLModel knows they exist
from app.db_models import User, Workspace, Project, Task

if __name__ == "__main__":
    print("Creating database tables...")
    create_db_and_tables()
    print("✅ Tables created successfully!")