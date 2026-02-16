from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from ..database.session import get_session
from ..models.user import User
from ..schemas.user import UserRead
from ..utils.jwt import get_current_user, TokenData
import uuid

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def get_current_user_profile(
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get the profile of the authenticated user
    """
    try:
        user_id = uuid.UUID(current_user.user_id)

        # Query user by ID
        statement = select(User).where(User.id == user_id)
        user = session.exec(statement).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Convert SQLModel object to Pydantic object
        user_dict = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "last_login_at": user.last_login_at,
            "is_active": user.is_active,
            "email_verified": user.email_verified
        }

        return UserRead(**user_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving user profile: {str(e)}"
        )