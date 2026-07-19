from sqlalchemy import  create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings
from urllib.parse import quote_plus




encoded_password = quote_plus(settings.db_password)

DATABASE_URL =  (f"mysql+pymysql://"
                 f"{settings.db_user}:"
                 f"{encoded_password}@"
                 f"{settings.db_host}:"
                 f"{settings.db_port}/"
                 f"{settings.db_name}")


engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    
    try: 
        print("Database Connected..")
        yield db
    finally :
        print("Database session closed")
        db.close()
        