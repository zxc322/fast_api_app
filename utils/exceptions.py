from starlette.exceptions import HTTPException

class CustomError(HTTPException):
    def __init__(self, id: int = None):
        if id:
            super().__init__(
                status_code=404,
                detail="User with id {} doesn't exists.".format(id)
                )
        else:
            super().__init__(
                status_code=400,
                detail="User with this email already exists in the system."
                )