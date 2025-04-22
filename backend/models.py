from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base  

# username:password@path:port/database?
URL_DATABASE = "postgresql://torenlong:postgres@localhost:5432/StreakCounter" 

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

