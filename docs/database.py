from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class CodeReview(Base):
    __tablename__ = "code_reviews"

    id = Column(Integer, primary_key=True, index=True)
    pr_number = Column(Integer, nullable=False)
    repo_name = Column(String, nullable=False)
    pr_title = Column(String)
    files_reviewed = Column(Integer)
    suggestions_given = Column(Integer)
    ai_provider = Column(String)
    review_duration = Column(Integer)  # in seconds
    status = Column(String)  # success, failed, partial
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Store the actual suggestions
    suggestions_json = Column(JSON)

class GitHubEvent(Base):
    __tablename__ = "github_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)
    repo_name = Column(String, nullable=False)
    pr_number = Column(Integer)
    payload = Column(JSON)
    processed = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database setup
DATABASE_URL = "sqlite:///./code_reviews.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()