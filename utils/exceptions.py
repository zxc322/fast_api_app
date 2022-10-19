from starlette.exceptions import HTTPException

class CustomError(HTTPException):
    def __init__(self, id: int = None, email: str = None, wrong_password: bool = False, user_exists: bool = False):
        print('from excep', id, email, wrong_password)
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