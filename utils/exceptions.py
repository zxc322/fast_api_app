from starlette.exceptions import HTTPException
from fastapi import status, HTTPException as fastapiException
from schemas.user import UserRsposneId



class MyExceptions:
    def __init__(self) -> None:
        self.exc = fastapiException

    async def permission_denied(self): 
        return self.exc(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You don't have perrmissions for this action."
    )

    async def credentials_exception(self):
        return self.exc(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    async def id_is_0(self):
        return self.exc(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Id can't be 0"
    )


    async def blocked(self): 
        return self.exc(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="This user have blocked invites from your company."
    )

    async def invited_already(self): 
        return self.exc(
        status_code=status.HTTP_409_CONFLICT,
        detail="This user is invited already."
    )

    async def active_already(self): 
        return self.exc(
        status_code=status.HTTP_409_CONFLICT,
        detail="You are an acvtive member of this company already."
    )

    async def not_active_yet(self): 
        return self.exc(
        status_code=status.HTTP_409_CONFLICT,
        detail="This user is not active member yet."
    )

    async def is_admin_already(self): 
        return self.exc(
        status_code=status.HTTP_409_CONFLICT,
        detail="This user is admin already."
    )

    async def is_not_admin_yet(self): 
        return self.exc(
        status_code=status.HTTP_409_CONFLICT,
        detail="This user is not admin yet."
    )

    async def you_just_may_not(self): 
        return self.exc(
        status_code=status.HTTP_409_CONFLICT,
        detail="You may not request member status in this company."
    )

    async def not_requested(self): 
        return self.exc(
        status_code=status.HTTP_409_CONFLICT,
        detail="This user did not made a request for member status."
    )
    
    async def question_was_not_found(self, id: int):
        return self.exc(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Question with id {id} wasn't found."
    )

    async def option_was_not_found(self, id: int):
        return self.exc(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Option with id {id} wasn't found."
    )

    async def low_options_quantity(self, id: int):
        return self.exc(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"Can't be less then 2 options in question (question id: {id})."
    )

    async def low_questions_quantity(self, id: int):
        return self.exc(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"Can't be less then 2 questions in quiz (quiz id: {id})."
    )

    async def quiz_not_found(self, id: int):
        return self.exc(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Quiz with id {id} wasn't found."
    )

    async def quiz_already_exists(self, name):
        return self.exc(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"Quiz witn name <{name}> already exists in this company."
    )

    async def question_already_exists(self, name):
        return self.exc(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"Question <{name}> already exists in this quiz."
    )


class CustomError(HTTPException):
    def __init__(self, id: int = None, 
        email: str = None, 
        wrong_password: bool = False, 
        user_exists: bool = False, 
        company_exists: bool = False,
        company_id: int = None,
        wrong_member_id: bool = False,
        not_unique_quiz_name: bool = False):

        if id:
            super().__init__(
                status_code=404,
                detail="User with id {} doesn't exists.".format(id)
                )
        elif email:
            super().__init__(
                status_code=404,
                detail="User with email {} doesn't exists.".format(email)
                )
        elif wrong_password:
            super().__init__(
                status_code=400,
                detail="Wrong password."
                )
        elif user_exists:
            super().__init__(
                status_code=400,
                detail="User with this email already exists in the system."
                )
        elif company_exists:
            super().__init__(
                status_code=400,
                detail="Company with this name already exists in the system."
                )
        elif company_id:
            super().__init__(
                status_code=404,
                detail="Company with id {} doesn't exists.".format(company_id)
                )
        elif wrong_member_id:
            super().__init__(
                status_code=404,
                detail="Data was't found"
                )
        # elif not_unique_quiz_name:
        #     super().__init__(
        #         status_code=409,
        #         detail='Quiz with this name already exists.'
        #         )