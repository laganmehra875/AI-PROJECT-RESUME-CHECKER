import os
import certifi
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Use environment variable for database URL, with the existing one as fallback
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://MeTkVrjhT5xQnyt.root:SAcwttISvQnn2ri9@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/test")

# Use a robust SSL certificate path
SSL_CA_PATH = os.getenv("SSL_CA_PATH", certifi.where())

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "ssl": {
            "ca": SSL_CA_PATH,
        }
    }
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()