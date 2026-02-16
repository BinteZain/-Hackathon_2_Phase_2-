from sqlalchemy import create_engine
from sqlmodel import Session
from .config import settings

# Create the SQLAlchemy engine
engine = create_engine(settings.DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session