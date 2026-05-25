from sqlalchemy.orm import Session
from app.database import Sessionlocal

from collections.abc import Generator

def get_db() -> Generator[Session, None, None]:
    db: Session = Sessionlocal()

    try:
        yield db
    finally:
        db.close()