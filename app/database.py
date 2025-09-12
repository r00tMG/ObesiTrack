import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DB_URL", "sqlite:///./data/obesitrack_db.sqlite3")

engine = create_engine(DATABASE_URL,connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# Session de la base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()