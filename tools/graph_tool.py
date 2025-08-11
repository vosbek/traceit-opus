from strands import tool
import os
from neo4j import GraphDatabase
from typing import Dict, List, Any

@tool(name="graph_lookup", desc="Query Neo4j for Struts action to JSP mappings and code relationships.")
def graph_lookup(lookup_type: str, key: str) -> Dict[str, Any]:
    """
    Query the Neo4j graph database for code relationships.
    
    Args:
        lookup_type: Type of lookup - 'action_to_jsp', 'jsp_to_action', 'file_relationships'
        key: The key to search for (action name, JSP path, etc.)
    """
    
    # Get Neo4j credentials
    uri = os.getenv("NEO4J_URL", "bolt://neo4j:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASS", "test")
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        with driver.session() as session:
            if lookup_type == "action_to_jsp":
                query = """
                MATCH (a:Action {name: $key})-[:FORWARDS_TO|INCLUDES]->(j:JSP)
                RETURN a.name as action, j.path as jsp_path, j.repo as repo
                """
                result = session.run(query, key=key)
                
            elif lookup_type == "jsp_to_action":
                query = """
                MATCH (j:JSP {path: $key})<-[:FORWARDS_TO|INCLUDES]-(a:Action)
                RETURN a.name as action, j.path as jsp_path, a.repo as repo
                """
                result = session.run(query, key=key)
                
            elif lookup_type == "file_relationships":
                query = """
                MATCH (f:File {path: $key})-[r]-(related)
                RETURN f.path as file_path, type(r) as relationship, 
                       related.path as related_path, labels(related) as related_type
                LIMIT 20
                """
                result = session.run(query, key=key)
                
            else:
                return {"error": f"Unknown lookup_type: {lookup_type}"}
            
            # Convert results to list of dictionaries
            records = []
            for record in result:
                records.append(dict(record))
            
            driver.close()
            
            return {
                "lookup_type": lookup_type,
                "key": key,
                "results": records,
                "count": len(records)
            }
            
    except Exception as e:
        return {"error": f"Neo4j query failed: {str(e)}"}


@tool(name="find_struts_mapping", desc="Find Struts action configuration and JSP mappings.")
def find_struts_mapping(action_path: str) -> Dict[str, Any]:
    """
    Find Struts configuration for a given action path.
    
    Args:
        action_path: The action path like '/iApp/ssc/clientAccounts/fixedLife/summary.action'
    """
    
    # Extract action name from path
    action_name = action_path.split('/')[-1].replace('.action', '')
    
    # Try multiple lookup strategies
    results = {}
    
    # Look for direct action mapping
    action_result = graph_lookup("action_to_jsp", action_name)
    if not action_result.get("error") and action_result.get("results"):
        results["direct_mapping"] = action_result
    
    # Look for path-based mapping
    path_result = graph_lookup("action_to_jsp", action_path)
    if not path_result.get("error") and path_result.get("results"):
        results["path_mapping"] = path_result
    
    # Search for related files
    if "summary" in action_name:
        summary_result = graph_lookup("file_relationships", "*summary*")
        if not summary_result.get("error") and summary_result.get("results"):
            results["related_files"] = summary_result
    
    return {
        "action_path": action_path,
        "action_name": action_name,
        "mappings": results
    }
