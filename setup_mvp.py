#!/usr/bin/env python3
"""
Quick setup script to populate Neo4j with basic Struts/JSP mappings.
Run this after starting the containers to get graph relationships working.
"""

import os
import sys
from neo4j import GraphDatabase

def setup_neo4j_schema():
    """Create basic schema and sample data for MVP."""
    
    uri = os.getenv("NEO4J_URL", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j") 
    password = os.getenv("NEO4J_PASS", "test")
    
    print(f"Connecting to Neo4j at {uri}...")
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        with driver.session() as session:
            # Clear existing data
            print("Clearing existing data...")
            session.run("MATCH (n) DETACH DELETE n")
            
            # Create constraints
            print("Creating constraints...")
            session.run("CREATE CONSTRAINT action_name IF NOT EXISTS FOR (a:Action) REQUIRE a.name IS UNIQUE")
            session.run("CREATE CONSTRAINT jsp_path IF NOT EXISTS FOR (j:JSP) REQUIRE j.path IS UNIQUE")
            session.run("CREATE CONSTRAINT file_path IF NOT EXISTS FOR (f:File) REQUIRE f.path IS UNIQUE")
            
            # Add sample Struts actions based on golden questions
            print("Adding sample Struts actions...")
            
            # Universal Life summary action
            session.run("""
                CREATE (a:Action {
                    name: 'summary',
                    path: '/iApp/ssc/clientAccounts/fixedLife/summary.action',
                    repo: 'legacy-web'
                })
            """)
            
            # Document center action  
            session.run("""
                CREATE (a:Action {
                    name: 'documentCenter',
                    path: '/iApp/ssc/documentCenter.action',
                    repo: 'legacy-web'
                })
            """)
            
            # Add JSP files
            print("Adding JSP files...")
            
            session.run("""
                CREATE (j:JSP {
                    path: '/WEB-INF/icm/jsp/policy/clientAccountBusiness/summary/fixedLife/loadedHeader.jsp',
                    repo: 'legacy-web',
                    type: 'Universal Life Header'
                })
            """)
            
            session.run("""
                CREATE (j:JSP {
                    path: '/WEB-INF/icm/jsp/policy/clientAccountBusiness/summary/fixedLife/summary.jsp', 
                    repo: 'legacy-web',
                    type: 'Universal Life Summary'
                })
            """)
            
            # Create relationships
            print("Creating relationships...")
            
            session.run("""
                MATCH (a:Action {name: 'summary'}), (j:JSP {path: '/WEB-INF/icm/jsp/policy/clientAccountBusiness/summary/fixedLife/loadedHeader.jsp'})
                CREATE (a)-[:INCLUDES]->(j)
            """)
            
            session.run("""
                MATCH (a:Action {name: 'summary'}), (j:JSP {path: '/WEB-INF/icm/jsp/policy/clientAccountBusiness/summary/fixedLife/summary.jsp'})
                CREATE (a)-[:FORWARDS_TO]->(j)
            """)
            
            # Add some database table nodes for reference
            print("Adding database references...")
            
            session.run("""
                CREATE (t:Table {
                    name: 'agreement_values',
                    schema: 'cppf',
                    purpose: 'Stores contract values including death benefits'
                })
            """)
            
            session.run("""
                CREATE (t:Table {
                    name: 'users',
                    schema: 'iwdb', 
                    purpose: 'User account information'
                })
            """)
            
            # Link JSPs to database tables they use
            session.run("""
                MATCH (j:JSP {path: '/WEB-INF/icm/jsp/policy/clientAccountBusiness/summary/fixedLife/summary.jsp'}),
                      (t:Table {name: 'agreement_values'})
                CREATE (j)-[:QUERIES]->(t)
            """)
            
            print("Setup complete!")
            
            # Verify data
            result = session.run("MATCH (n) RETURN labels(n) as type, count(n) as count")
            print("\nCreated nodes:")
            for record in result:
                print(f"  {record['type']}: {record['count']}")
                
        driver.close()
        
    except Exception as e:
        print(f"Error setting up Neo4j: {e}")
        return False
        
    return True

def populate_sample_code_index():
    """Add some sample code documents to OpenSearch for testing."""
    from retrievers.pipeline import upsert
    
    print("Adding sample code documents to OpenSearch...")
    
    # Sample JSP content for Universal Life
    upsert({
        "id": "jsp_ul_header",
        "kind": "jsp",
        "repo": "legacy-web",
        "path": "/WEB-INF/icm/jsp/policy/clientAccountBusiness/summary/fixedLife/loadedHeader.jsp",
        "sha": "abc123",
        "source_env": "legacy",
        "anchors": ["Universal Life", "Account Information", "loadedHeader"],
        "text": """<%-- Universal Life Account Information Header --%>
<div class="account-header">
    <h2>Universal Life Contract Information</h2>
    <div class="contract-details">
        <span>Product Sub Type: ${productSubType}</span>
        <span>Life Contract Type: ${lifeContractType}</span>
    </div>
</div>"""
    })
    
    # Sample JSP with contract options
    upsert({
        "id": "jsp_contract_options",
        "kind": "jsp", 
        "repo": "legacy-web",
        "path": "/WEB-INF/icm/jsp/policy/clientAccountBusiness/summary/fixedLife/contractOptions.jsp",
        "sha": "def456",
        "source_env": "legacy",
        "anchors": ["contract options", "UL", "specified amount", "plan name"],
        "text": """<%-- Contract Options Section --%>
<div class="contract-options">
    <h3>Primary Coverage</h3>
    <div class="field-group">
        <label>Plan Name:</label>
        <span>${contractOptions.planName}</span>
    </div>
    <div class="field-group">
        <label>Insured:</label>
        <span>${contractOptions.insured}</span>
    </div>
    <div class="field-group">
        <label>Specified Amount:</label>
        <span>${contractOptions.specifiedAmount}</span>
    </div>
    <div class="field-group">
        <label>Issue Age:</label>
        <span>${contractOptions.issueAge}</span>
    </div>
    
    <h3>Additional Coverage</h3>
    <div class="benefits-section">
        <c:forEach var="benefit" items="${contractOptions.benefits}" varStatus="status">
            <div class="benefit-item">
                <label>${benefit.name}:</label>
                <span>${benefit.value}</span>
            </div>
        </c:forEach>
    </div>
</div>"""
    })
    
    # Sample Struts configuration
    upsert({
        "id": "struts_summary_action",
        "kind": "xml",
        "repo": "legacy-web", 
        "path": "/WEB-INF/struts-config.xml",
        "sha": "ghi789",
        "source_env": "legacy",
        "anchors": ["summary", "fixedLife", "action", "documentCenter"],
        "text": """<struts-config>
    <action-mappings>
        <action path="/iApp/ssc/clientAccounts/fixedLife/summary"
                type="com.nw.ssc.web.actions.SummaryAction"
                name="summaryForm"
                scope="request">
            <forward name="success" path="/WEB-INF/icm/jsp/policy/clientAccountBusiness/summary/fixedLife/summary.jsp"/>
            <forward name="header" path="/WEB-INF/icm/jsp/policy/clientAccountBusiness/summary/fixedLife/loadedHeader.jsp"/>
        </action>
        
        <action path="/iApp/ssc/documentCenter"
                type="com.nw.ssc.web.actions.DocumentCenterAction"
                name="documentForm">
            <forward name="success" path="/WEB-INF/icm/jsp/documentCenter.jsp"/>
        </action>
    </action-mappings>
</struts-config>"""
    })
    
    # Sample Java action class
    upsert({
        "id": "java_summary_action",
        "kind": "java",
        "repo": "legacy-web",
        "path": "com/nw/ssc/web/actions/SummaryAction.java", 
        "sha": "jkl012",
        "source_env": "legacy",
        "anchors": ["SummaryAction", "contractOptions", "agreement_values", "DEATH BENEFIT AMOUNT"],
        "text": """package com.nw.ssc.web.actions;

public class SummaryAction extends BaseAction {
    
    public ActionForward execute(ActionMapping mapping, ActionForm form, 
                               HttpServletRequest request, HttpServletResponse response) {
        
        // Get contract options from database
        ContractOptions contractOptions = getContractOptions(request);
        
        // Query agreement_values for specified amount
        String specifiedAmount = dbService.queryValue(
            "SELECT value FROM agreement_values WHERE value_type = 'DEATH BENEFIT AMOUNT' AND agreement_id = ?",
            agreementId
        );
        
        contractOptions.setSpecifiedAmount(specifiedAmount);
        request.setAttribute("contractOptions", contractOptions);
        
        return mapping.findForward("success");
    }
}"""
    })
    
    print("Sample code documents added to OpenSearch!")

if __name__ == "__main__":
    print("Setting up Legacy Codebase Assistant MVP...")
    
    # Setup Neo4j
    if setup_neo4j_schema():
        print("✓ Neo4j setup complete")
    else:
        print("✗ Neo4j setup failed")
        sys.exit(1)
    
    # Setup OpenSearch with sample data
    try:
        populate_sample_code_index()
        print("✓ OpenSearch sample data added")
    except Exception as e:
        print(f"✗ OpenSearch setup failed: {e}")
    
    print("\nMVP setup complete! You can now test queries.")
    print("\nTry these sample queries:")
    print("1. Where does 'Specified Amount' come from on the summary action?")
    print("2. What JSP contains the code that displays Account Information for Universal Life?")
    print("3. What are the contract options for UL contracts?")
