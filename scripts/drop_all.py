from sqlalchemy import create_engine, MetaData
import os
from dotenv import load_dotenv

load_dotenv()

# 'postgresql://username:password@host:port/database_name'
postgres_uri = os.getenv("SQLALCHEMY_DATABASE_URI")

def drop_all(uri):
    engine = create_engine(uri)
    metadata = MetaData(bind=engine)
    
    metadata.reflect()
    
    reversed_tables = reversed(metadata.sorted_tables)
    for table in reversed_tables:
        print(table.name)
        table.drop(bind=engine)

if __name__ == "__main__":
    drop_all(postgres_uri)
