from typing import Optional
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import List

from db.models import User as DBUser
from schemas.user import User, UserCreate, UpdateUser
from security.auth import get_password_hash


def get_by_email(db_session: Session, email: str) -> Optional[DBUser]:
        return db_session.query(DBUser).filter(DBUser.email == email).first()

def get_by_id(db_session: Session, id: int) -> Optional[DBUser]:
        return db_session.query(DBUser).filter(DBUser.id == id).first()

def create(db_session: Session, user_in: UserCreate) -> DBUser:
        user = DBUser(
            username=user_in.username,
            email=user_in.email,
            password=get_password_hash(user_in.password2),
            about_me=user_in.about_me,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user


def update(db_session: Session, user: DBUser, user_in: UpdateUser) -> DBUser:
        user_data = jsonable_encoder(user)
        updated_data = user_in.dict(skip_defaults=True)
        if 'password' in updated_data.keys():
                print('yes')
                updated_data['password'] = get_password_hash(updated_data['password'])
        for field in user_data:
            if field in updated_data:
                setattr(user, field, updated_data[field])
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

def remove(db_session: Session, *, id: int) -> DBUser:
        user = db_session.query(DBUser).get(id)
        db_session.delete(user)
        db_session.commit()
        return user



