from typing import Optional
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Dict
import math

from db.models import User as DBUser
from schemas.user import UserCreate, UpdateUser, User
from security.auth import get_password_hash
from repositories.service import Log, paginate_data


class UserCRUD:
    
    @staticmethod
    def get_by_email(db_session: Session, email: str) -> Optional[DBUser]:
        return db_session.query(DBUser).filter(DBUser.email == email).first()
    
    @staticmethod
    def get_by_id(db_session: Session, id: int) -> Optional[DBUser]:
        return db_session.query(DBUser).filter(DBUser.id == id).first()

    @staticmethod
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

    @staticmethod
    def update(db_session: Session, user: DBUser, user_in: UpdateUser) -> DBUser:
        user_data = jsonable_encoder(user)
        updated_data = user_in.dict(skip_defaults=True)
        if 'password' in updated_data.keys():
                updated_data['password'] = get_password_hash(updated_data['password'])
        for field in user_data:
            if field in updated_data:

                with open('logs_database.log', 'a') as f:
                        f.write(Log.write_to_file_updated(
                                user_data['id'],
                                field,
                                user_data[field],
                                updated_data[field]
                        )) 

                setattr(user, field, updated_data[field])
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @staticmethod
    def remove(db_session: Session, id: int) -> DBUser:
        if db_session.query(DBUser).filter(DBUser.id == id).count():
                user = db_session.query(DBUser).get(id)
                db_session.delete(user)
                db_session.commit()

                with open('logs_database.log', 'a') as f:
                        f.write(Log.write_to_file_deleted(id))

                return user

    @staticmethod
    def get_users(db_session: Session, page: int = 1, limit: int = 10) -> Dict:
        if page<1:
                page = 1
        skip = (page-1) * limit
        end = skip + limit

        queryset = db_session.query(DBUser).offset(skip).limit(limit).all()
        count = db_session.query(DBUser).count()
        total_pages = math.ceil(count/limit)
        pagination = paginate_data(page, count, total_pages, end, limit)
        return {'users': queryset, 'pagination': pagination}
        
