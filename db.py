import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL missing. Add it to .env")

# Supabase requires SSL in most cases:
if "sslmode=" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL + ("&" if "?" in DATABASE_URL else "?") + "sslmode=require"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
