from app.db import engine
from app.models.db_models import Base

def init_db():
    Base.metadata.create_all(bind=engine)
