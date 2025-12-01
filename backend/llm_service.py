from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
import os
from dotenv import load_dotenv
import json
from typing import List, Dict, Any, Tuple
from langsmith import Client, traceable
from langsmith.run_helpers import get_current_run_tree

load_dotenv()

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Initialize LangSmith Client
        self.langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
        if self.langsmith_api_key:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
            os.environ["LANGCHAIN_API_KEY"] = self.langsmith_api_key
            os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "DB-QueryPilot-AI")
            self.langsmith_client = Client(api_key=self.langsmith_api_key)
            print("✅ LangSmith tracking enabled - Project: DB-QueryPilot-AI")
        else:
            print("⚠️ LangSmith API key not found. Tracking disabled.")
            self.langsmith_client = None
        
        # Initialize OpenAI with faster model and optimized settings
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo", 
            temperature=0,
            openai_api_key=self.api_key,
            max_tokens=500,
            request_timeout=10,
            # Enable callbacks for better tracing
            callbacks=None
        )
        
        # Optimized SQL Generation Prompt
        self.sql_prompt_template = """You are a SQL expert. Generate complete and valid SQL queries.

Schema:
{schema}

Task: {prompt}

IMPORTANT RULES:
1. For INSERT queries: Include ALL columns that cannot be NULL
2. For UPDATE/DELETE: Always include WHERE clause
3. Use CASE-INSENSITIVE comparisons: Use LOWER(column) = LOWER('value') for text comparisons
4. For category searches, use: LOWER(category) LIKE LOWER('%electronics%')
5. Check schema carefully for required fields
6. Use proper data types

Return ONLY this JSON format (no markdown, no backticks):
{{"sql_query": "your SQL here", "explanation": "brief description"}}"""
    
    @traceable(
        name="🔍 Get Available Tables",
        run_type="tool"
    )
    def get_databases(self, db: Session) -> List[str]:
        """Get list of databases/tables"""
        try:
            inspector = inspect(db.bind)
            tables = inspector.get_table_names()
            result = tables if tables else ["default"]
            print(f"📊 Found tables: {result}")
            return result
        except Exception as e:
            print(f"❌ Error getting tables: {str(e)}")
            return ["default"]
    
    @traceable(
        name="📋 Get Table Schema",
        run_type="tool",
        metadata={"purpose": "fetch_schema"}
    )
    def get_table_schemas(self, db: Session, database_name: str = None) -> List[Dict[str, Any]]:
        """Get schema information - cached for performance"""
        try:
            inspector = inspect(db.bind)
            tables_info = []
            
            for table_name in inspector.get_table_names():
                columns = []
                for column in inspector.get_columns(table_name):
                    columns.append({
                        "name": column["name"],
                        "type": str(column["type"]),
                        "nullable": column["nullable"]
                    })
                
                tables_info.append({
                    "name": table_name,
                    "columns": columns
                })
            
            print(f"📋 Retrieved schema for {len(tables_info)} tables")
            return tables_info
        except Exception as e:
            print(f"❌ Error getting schema: {str(e)}")
            return []
    
    @traceable(name="🔧 Format Schema for Prompt")
    def _format_schema_for_prompt(self, table_schemas: List[Dict[str, Any]]) -> str:
        """Schema format with nullable info for better SQL generation"""
        schema_str = ""
        for table in table_schemas:
            schema_str += f"\nTable: {table['name']}\nColumns:\n"
            for col in table['columns']:
                nullable = "NULL" if col['nullable'] else "NOT NULL (Required)"
                schema_str += f"  - {col['name']} ({col['type']}) {nullable}\n"
        return schema_str
    
    @traceable(
        name="🤖 Generate SQL from Natural Language",
        run_type="llm",
        metadata={
            "model": "gpt-3.5-turbo",
            "task": "text-to-sql",
            "temperature": 0
        }
    )
    async def generate_sql(
        self, 
        prompt: str, 
        table_schemas: List[Dict[str, Any]],
        user_id: str = None,
        session_id: str = None
    ) -> Tuple[str, str]:
        """Generate SQL query - optimized for speed with comprehensive LangSmith tracking"""
        
        # Add metadata to current run
        current_run = get_current_run_tree()
        if current_run:
            current_run.metadata.update({
                "user_prompt": prompt,
                "num_tables": len(table_schemas),
                "table_names": [t['name'] for t in table_schemas]
            })
            if user_id:
                current_run.metadata["user_id"] = user_id
            if session_id:
                current_run.metadata["session_id"] = session_id
        
        try:
            schema_str = self._format_schema_for_prompt(table_schemas)
            
            full_prompt = self.sql_prompt_template.format(
                schema=schema_str,
                prompt=prompt
            )
            
            print(f"💬 User Query: {prompt}")
            print(f"📝 Generating SQL...")
            
            # LLM invocation (automatically tracked by LangChain)
            response = self.llm.invoke(full_prompt)
            response_text = response.content.strip()
            
            print(f"✅ LLM Response received")
            
            # Parse JSON response
            try:
                # Remove markdown if present
                if response_text.startswith("```"):
                    response_text = response_text.split("```")[1]
                    if response_text.startswith("json"):
                        response_text = response_text[4:]
                
                response_text = response_text.strip()
                result = json.loads(response_text)
                
                sql_query = result.get("sql_query", "").strip()
                explanation = result.get("explanation", "Query generated")
                
                print(f"✅ Generated SQL: {sql_query}")
                
                # Add output to trace
                if current_run:
                    current_run.outputs = {
                        "sql_query": sql_query,
                        "explanation": explanation,
                        "success": True
                    }
                
                return sql_query, explanation
                
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON Parse Error: {str(e)}")
                # Fallback: extract SQL manually
                if "SELECT" in response_text.upper() or "INSERT" in response_text.upper():
                    return response_text, "Generated SQL query (parsed from text)"
                raise Exception("Could not parse SQL from response")
                
        except Exception as e:
            error_msg = f"Error generating SQL: {str(e)}"
            print(f"❌ {error_msg}")
            
            # Log error to trace
            if current_run:
                current_run.error = error_msg
                current_run.outputs = {"success": False, "error": str(e)}
            
            raise Exception(error_msg)
    
    @traceable(
        name="📊 Execute SELECT Query",
        run_type="tool",
        metadata={"operation": "read"}
    )
    def execute_query(self, db: Session, sql_query: str) -> List[Dict[str, Any]]:
        """Execute SELECT query - optimized with tracking"""
        
        current_run = get_current_run_tree()
        if current_run:
            current_run.metadata["sql_query"] = sql_query
        
        try:
            print(f"🔍 Executing query: {sql_query[:100]}...")
            
            result = db.execute(text(sql_query))
            columns = result.keys()
            rows = result.fetchall()
            
            # Fast list comprehension
            results = [
                {col: row[i] for i, col in enumerate(columns)}
                for row in rows
            ]
            
            print(f"✅ Query executed: {len(results)} rows returned")
            
            # Add to trace
            if current_run:
                current_run.outputs = {
                    "rows_returned": len(results),
                    "columns": list(columns),
                    "success": True
                }
            
            return results
            
        except Exception as e:
            error_msg = f"Error executing query: {str(e)}"
            print(f"❌ {error_msg}")
            
            if current_run:
                current_run.error = error_msg
                current_run.outputs = {"success": False, "error": str(e)}
            
            raise Exception(error_msg)
    
    @traceable(
        name="✏️ Execute Modification Query",
        run_type="tool",
        metadata={"operation": "write"}
    )
    def execute_modification(self, db: Session, sql_query: str) -> int:
        """Execute INSERT/UPDATE/DELETE - optimized with tracking"""
        
        current_run = get_current_run_tree()
        if current_run:
            current_run.metadata["sql_query"] = sql_query
            # Detect operation type
            if "INSERT" in sql_query.upper():
                current_run.metadata["operation_type"] = "INSERT"
            elif "UPDATE" in sql_query.upper():
                current_run.metadata["operation_type"] = "UPDATE"
            elif "DELETE" in sql_query.upper():
                current_run.metadata["operation_type"] = "DELETE"
        
        try:
            print(f"✏️ Executing modification: {sql_query[:100]}...")
            
            result = db.execute(text(sql_query))
            db.commit()
            affected = result.rowcount
            
            print(f"✅ Modification executed: {affected} rows affected")
            
            # Add to trace
            if current_run:
                current_run.outputs = {
                    "rows_affected": affected,
                    "success": True,
                    "committed": True
                }
            
            return affected
            
        except Exception as e:
            db.rollback()
            error_msg = f"Error: {str(e)}"
            print(f"❌ {error_msg}")
            
            if current_run:
                current_run.error = error_msg
                current_run.outputs = {
                    "success": False,
                    "error": str(e),
                    "rolled_back": True
                }
            
            raise Exception(error_msg)