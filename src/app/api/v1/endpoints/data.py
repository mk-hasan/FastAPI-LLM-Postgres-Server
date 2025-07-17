from fastapi import APIRouter, Depends, status, HTTPException
from app.models.db_models import UserDataCreate, UserDataRead
from app.services.data_service import DataService, get_data_service

router = APIRouter()

@router.post(
    "/users",
    response_model=UserDataRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user data",
    description="Creates a new user entry in the database."
)
def create_user_data_endpoint(
    user_data: UserDataCreate,
    data_service: DataService = Depends(get_data_service)
) -> UserDataRead:
    """
    Creates a new user record.
    """
    return data_service.create_user_data(user_data)

@router.get(
    "/users/{user_id}",
    response_model=UserDataRead,
    status_code=status.HTTP_200_OK,
    summary="Get user data by ID",
    description="Retrieves a single user's data from the database by their ID."
)
def get_user_data_endpoint(
    user_id: int,
    data_service: DataService = Depends(get_data_service)
) -> UserDataRead:
    """
    Retrieves a user record by its ID.
    Raises 404 if user not found.
    """
    user = data_service.get_user_data(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.get(
    "/users",
    response_model=list[UserDataRead],
    status_code=status.HTTP_200_OK,
    summary="Get all user data",
    description="Retrieves a list of all user entries from the database with pagination."
)
def get_all_user_data_endpoint(
    skip: int = 0,
    limit: int = 100,
    data_service: DataService = Depends(get_data_service)
) -> list[UserDataRead]:
    """
    Retrieves all user records with optional pagination.
    """
    return data_service.get_all_user_data(skip=skip, limit=limit)