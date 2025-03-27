"""
Database module for the CMS.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def get_engine(uri):
    """Get a SQLAlchemy engine."""
    return create_engine(uri)

def get_session_factory(engine):
    """Get a SQLAlchemy session factory."""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_scoped_session(session_factory):
    """Get a SQLAlchemy scoped session."""
    return scoped_session(session_factory)
