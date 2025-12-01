from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from dotenv import load_dotenv
from langsmith import traceable

load_dotenv()

DATABASE_URL = r"sqlite:///C:/Users/Kartik joshi/company_database.db"

# If DATABASE_URL is not set, use default path
if not DATABASE_URL:
    # Get the directory where this file is located
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(BASE_DIR, "company_database.db")
    DATABASE_URL = f"sqlite:///{db_path}"

print(f"🗄️ Database URL: {DATABASE_URL}")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True  # This will print SQL queries for debugging
    )
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

@traceable(
    name="💾 Database Session",
    run_type="tool",
    metadata={"operation": "get_db_session"}
)
def get_db():
    """Get database session with LangSmith tracking"""
    db = SessionLocal()
    try:
        print("✅ Database session created")
        yield db
    finally:
        db.close()
        print("🔒 Database session closed")

@traceable(
    name="📊 Get Table Info",
    run_type="tool",
    metadata={"operation": "inspect_tables"}
)
def get_table_info(db_engine):
    """Get comprehensive table information with LangSmith tracking"""
    try:
        inspector = inspect(db_engine)
        tables_info = {}
        
        for table_name in inspector.get_table_names():
            columns = []
            for column in inspector.get_columns(table_name):
                columns.append({
                    "name": column["name"],
                    "type": str(column["type"]),
                    "nullable": column["nullable"],
                    "default": column.get("default"),
                    "primary_key": column.get("primary_key", False)
                })
            
            tables_info[table_name] = {
                "columns": columns
            }
        
        print(f"✅ Retrieved info for {len(tables_info)} tables")
        return tables_info
        
    except Exception as e:
        print(f"❌ Error getting table info: {str(e)}")
        raise