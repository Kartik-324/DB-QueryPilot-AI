from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from database import get_db, engine
from llm_service import LLMService
import logging
from langsmith import traceable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="DB QueryPilot AI", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM Service
llm_service = LLMService()

# Pydantic models
class QueryRequest(BaseModel):
    prompt: str
    database_name: str
    execute: bool = False

class QueryResponse(BaseModel):
    sql_query: str
    explanation: str
    results: Optional[List[Dict[str, Any]]] = None
    success: bool
    message: str

class TableInfo(BaseModel):
    name: str
    columns: List[Dict[str, str]]

@app.get("/")
async def root():
    return {
        "message": "RAG-based SQL Query API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/databases", response_model=List[str])
async def get_databases(db: Session = Depends(get_db)):
    """Get list of all accessible databases/tables"""
    try:
        databases = llm_service.get_databases(db)
        return databases
    except Exception as e:
        logger.error(f"Error fetching databases: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tables/{database}", response_model=List[TableInfo])
async def get_tables(database: str, db: Session = Depends(get_db)):
    """Get all tables with their schema"""
    try:
        tables = llm_service.get_table_schemas(db, database)
        return tables
    except Exception as e:
        logger.error(f"Error fetching tables: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
@traceable(
    name="🎯 User Query - End to End",
    run_type="chain",
    metadata={"endpoint": "/query", "type": "select"}
)
async def generate_query(request: QueryRequest, db: Session = Depends(get_db)):
    """Generate SQL query from natural language prompt"""
    try:
        logger.info(f"📥 Received query request: {request.prompt}")
        
        # Get table schemas for context
        table_schemas = llm_service.get_table_schemas(db, request.database_name)
        
        # Generate SQL query using LLM
        sql_query, explanation = await llm_service.generate_sql(
            prompt=request.prompt,
            table_schemas=table_schemas
        )
        
        response = QueryResponse(
            sql_query=sql_query,
            explanation=explanation,
            success=True,
            message="SQL query generated successfully"
        )
        
        # Execute if requested
        if request.execute:
            results = llm_service.execute_query(db, sql_query)
            response.results = results
            response.message = f"Query executed successfully. {len(results)} rows returned."
            logger.info(f"✅ Query executed: {len(results)} rows")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Error generating query: {str(e)}")
        return QueryResponse(
            sql_query="",
            explanation="",
            success=False,
            message=f"Error: {str(e)}"
        )

@app.post("/execute")
@traceable(
    name="✏️ Database Modification - End to End",
    run_type="chain",
    metadata={"endpoint": "/execute", "type": "modification"}
)
async def execute_query(request: QueryRequest, db: Session = Depends(get_db)):
    """Execute SQL query directly (for modifications)"""
    try:
        logger.info(f"📥 Received modification request: {request.prompt}")
        
        # Get table schemas for context
        table_schemas = llm_service.get_table_schemas(db, request.database_name)
        
        # Generate SQL query
        sql_query, explanation = await llm_service.generate_sql(
            prompt=request.prompt,
            table_schemas=table_schemas
        )
        
        logger.info(f"Generated SQL for modification: {sql_query}")
        
        # Check if query is a modification query
        is_modification = any(keyword in sql_query.upper() for keyword in ['INSERT', 'UPDATE', 'DELETE'])
        
        if is_modification:
            # Execute modification
            affected_rows = llm_service.execute_modification(db, sql_query)
            logger.info(f"✅ Modification executed. Rows affected: {affected_rows}")
            
            return {
                "sql_query": sql_query,
                "explanation": explanation,
                "affected_rows": affected_rows,
                "success": True,
                "message": f"✅ Query executed successfully. {affected_rows} rows affected."
            }
        else:
            # Execute select query
            results = llm_service.execute_query(db, sql_query)
            return {
                "sql_query": sql_query,
                "explanation": explanation,
                "results": results,
                "success": True,
                "message": f"Query executed successfully. {len(results)} rows returned."
            }
            
    except Exception as e:
        logger.error(f"❌ Error executing query: {str(e)}")
        return {
            "sql_query": "",
            "explanation": "",
            "success": False,
            "message": f"Error: {str(e)}"
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "RAG SQL API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)