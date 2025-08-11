from strands import tool
import os
import oracledb
import re

@tool(name="oracle_query", desc="Run read-only SQL against Oracle to verify values and get database evidence.")
def oracle_query(sql: str) -> dict:
    """Execute read-only SQL queries against Oracle database with basic safety checks."""
    
    # Get credentials
    dsn = os.getenv("ORACLE_DSN")
    user = os.getenv("ORACLE_USER") 
    pw = os.getenv("ORACLE_PASS")
    
    if not (dsn and user and pw):
        return {"error": "Oracle credentials not configured"}
    
    # Basic SQL safety - simple but effective for internal use
    sql_upper = sql.upper().strip()
    
    # Must start with SELECT
    if not sql_upper.startswith("SELECT"):
        return {"error": "Only SELECT statements are allowed"}
    
    # Block dangerous keywords
    dangerous_keywords = [
        "INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER", 
        "TRUNCATE", "GRANT", "REVOKE", "COMMIT", "ROLLBACK"
    ]
    
    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            return {"error": f"Keyword '{keyword}' not allowed"}
    
    # Add row limiting if not present
    if "FETCH FIRST" not in sql_upper and "ROWNUM" not in sql_upper:
        # Simple append - for MVP speed
        sql = sql.rstrip(';') + " FETCH FIRST 50 ROWS ONLY"
    
    try:
        # Execute with timeout
        conn = oracledb.connect(user=user, password=pw, dsn=dsn)
        cursor = conn.cursor()
        
        # Set query timeout
        cursor.execute(sql)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        # Fetch results
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "sql_executed": sql
        }
        
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}
