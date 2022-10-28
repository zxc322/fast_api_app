from email.policy import default
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    username = Column(String)
    password = Column(String)
    about_me = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, default=None, nullable=True)
    updated_by = Column(Integer, nullable=True) 

    company = relationship("Company")
    members = relationship("CompanyMembers")  


class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String(555), nullable=True)
    visible = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, default=None, nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="company")
    company_relation = relationship("CompanyMembers")
    quiz = relationship("Quiz", cascade="all, delete")


class CompanyMembers(Base):
    __tablename__ = 'company_members'

    id = Column(Integer, primary_key=True, index=True)
    active_member = Column(DateTime, nullable=True, default=None)
    invited = Column(DateTime, nullable=True, default=None)
    requested = Column(DateTime, nullable=True, default=None)
    ignored_by_user = Column(Boolean, default=False)
    ignored_by_owner = Column(Boolean, default=False)
    is_company_admin = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    

    company_id = Column(Integer, ForeignKey("companies.id"))
    member_id = Column(Integer, ForeignKey("users.id"))

    company = relationship("Company", back_populates="company_relation")
    member = relationship("User", back_populates="members")


class Quiz(Base):
    __tablename__ = 'quiz'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String, nullable=True)
    frequency = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, default=None, nullable=True)
        
    company_id = Column(Integer, ForeignKey("companies.id"))

    question = relationship("Question")
    company = relationship("Company", back_populates="quiz")

class Question(Base):
    __tablename__ = 'question'

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String)
    deleted_at = Column(DateTime, default=None, nullable=True)

    quiz_id = Column(Integer, ForeignKey("quiz.id"))

    quiz = relationship("Quiz", back_populates="question")
    option = relationship("Option", cascade="all, delete")
    

class Option(Base):
    __tablename__ = 'option'

    id = Column(Integer, primary_key=True, index=True)
    option = Column(String)
    is_right = Column(Boolean, default=False)

    question_id = Column(Integer, ForeignKey("question.id"))
    question = relationship("Question", back_populates="option")


    

users = User.__table__
companies = Company.__table__
company_members = CompanyMembers.__table__
quiz = Quiz.__table__
question = Question.__table__
option = Option.__table__
