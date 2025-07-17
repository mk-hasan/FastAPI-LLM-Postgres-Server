from sqlalchemy.orm import Session
from app.db.models import UserData as DBUserData
from app.models.db_models import UserDataCreate, UserDataRead
from fastapi import Depends # <--- ADD THIS LINE

class DataService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_data(self, user_id: int) -> UserDataRead | None:
        """Fetches user data by ID."""
        user = self.db.query(DBUserData).filter(DBUserData.id == user_id).first()
        return UserDataRead.model_validate(user) if user else None

    def create_user_data(self, user_data: UserDataCreate) -> UserDataRead:
        """Creates new user data."""
        db_user = DBUserData(**user_data.model_dump())
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return UserDataRead.model_validate(db_user)

    def get_all_user_data(self, skip: int = 0, limit: int = 100) -> list[UserDataRead]:
        """Fetches a list of all user data."""
        users = self.db.query(DBUserData).offset(skip).limit(limit).all()
        return [UserDataRead.model_validate(user) for user in users]

# You also need to import get_db and get_settings here if you're using them
from app.db.database import get_db # <--- ADD THIS LINE if not already present
# Dependency for DataService
def get_data_service(db: Session = Depends(get_db)):
    return DataService(db)