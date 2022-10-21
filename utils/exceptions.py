from starlette.exceptions import HTTPException
from fastapi import status, HTTPException as fastapiException
from schemas.user import UserRsposneId

class CustomError(HTTPException):
    def __init__(self, id: int = None, email: str = None, wrong_password: bool = False, user_exists: bool = False):
        if id:
            super().__init__(
                status_code=404,
                detail="User with id {} doesn't exists.".format(id)
                )
        if email:
            super().__init__(
                status_code=404,
                detail="User with email {} doesn't exists.".format(email)
                )
        if wrong_password:
            super().__init__(
                status_code=400,
                detail="Wrong password."
                )
        if user_exists:
            super().__init__(
                status_code=400,
                detail="User with this email already exists in the system."
                )

credentials_exception = fastapiException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

permission_denied = fastapiException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You don't perrmissions for this action."
    )


def permission_validator(id: int, user: UserRsposneId):
    if isinstance(user, dict):
        raise credentials_exception        
    if user.id != id:
        raise permission_denied