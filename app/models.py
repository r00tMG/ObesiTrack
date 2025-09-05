import enum

from sqlalchemy import Column, Integer, String, DateTime, func, Enum

from app.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

class User(Base):
    __tablename__ ="users"
    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String)
    email = Column(String)
    password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.USER)
    created_at = Column(DateTime(timezone=True), server_default=func.now())