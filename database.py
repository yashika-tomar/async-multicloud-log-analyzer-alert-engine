from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define file storage path. SQLite stores everything safely in an unmanaged local system file called app.db
DATABASE_URL = "sqlite:///./app.db?check_same_thread=False"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AnomalyRecord(Base):
    """Relational SQL model schema mapping for tracking persistent anomalies."""
    __tablename__ = "anomaly_records"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, index=True)
    ip_address = Column(String)
    timestamp = Column(String)
    method = Column(String)
    path = Column(String)
    status_code = Column(String)

# Database initializer routine to automatically create files and schema tables
def init_db():
    Base.metadata.create_all(bind=engine)