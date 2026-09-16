from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from urllib.parse import quote_plus
from app.core.database import Base
from app.models import *



encoded_password = quote_plus(settings.db_password)

TEST_DATABASE_URL = (
    f"mysql+pymysql://"
    f"{settings.db_user}:"
    f"{encoded_password}@"
    f"{settings.db_host}:"
    f"{settings.db_port}/"
    f"ecommerce_test_db"
)

test_engine = create_engine(TEST_DATABASE_URL, echo=True)


TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


print(Base.metadata.tables.keys())

Base.metadata.create_all(bind=test_engine)