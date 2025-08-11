#!/usr/bin/env python3
"""
Index application documentation and additional sources into OpenSearch.
This script should be run to add documentation beyond code.
"""

import os
import glob
from retrievers.pipeline import upsert
from pathlib import Path

def index_documentation(docs_path: str):
    """Index documentation files from a directory."""
    
    if not os.path.exists(docs_path):
        print(f"Documentation path does not exist: {docs_path}")
        return
    
    print(f"Indexing documentation from: {docs_path}")
    
    # Supported documentation formats
    doc_patterns = [
        "*.md", "*.txt", "*.rst", "*.doc", "*.docx", 
        "*.pdf", "*.html", "*.wiki"
    ]
    
    doc_count = 0
    
    for pattern in doc_patterns:
        for file_path in glob.glob(os.path.join(docs_path, "**", pattern), recursive=True):
            try:
                # Read file content
                content = read_file_content(file_path)
                if not content:
                    continue
                
                # Generate document ID
                rel_path = os.path.relpath(file_path, docs_path)
                doc_id = f"doc_{rel_path.replace(os.sep, '_').replace('.', '_')}"
                
                # Extract keywords/anchors from filename and content
                anchors = extract_anchors(file_path, content)
                
                # Create document
                doc = {
                    "id": doc_id,
                    "kind": "documentation",
                    "repo": "documentation",
                    "path": rel_path,
                    "sha": "latest",
                    "source_env": "legacy",
                    "anchors": anchors,
                    "text": content
                }
                
                upsert(doc)
                doc_count += 1
                print(f"  Indexed: {rel_path}")
                
            except Exception as e:
                print(f"  Error indexing {file_path}: {e}")
    
    print(f"Indexed {doc_count} documentation files")

def read_file_content(file_path: str) -> str:
    """Read content from various file types."""
    
    file_ext = Path(file_path).suffix.lower()
    
    try:
        if file_ext in ['.md', '.txt', '.rst', '.html']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif file_ext == '.pdf':
            # For PDF files, you'd need PyPDF2 or similar
            # For MVP, skip PDFs or implement if needed
            print(f"  Skipping PDF: {file_path} (not implemented)")
            return ""
        
        elif file_ext in ['.doc', '.docx']:
            # For Word docs, you'd need python-docx
            # For MVP, skip or implement if needed  
            print(f"  Skipping Word doc: {file_path} (not implemented)")
            return ""
        
        else:
            # Try to read as text
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
                
    except Exception as e:
        print(f"  Error reading {file_path}: {e}")
        return ""

def extract_anchors(file_path: str, content: str) -> list:
    """Extract keywords and anchors from documentation."""
    
    anchors = []
    
    # Add filename-based anchors
    filename = Path(file_path).stem
    anchors.extend(filename.replace('_', ' ').replace('-', ' ').split())
    
    # Extract headers (markdown style)
    import re
    headers = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
    for header in headers:
        anchors.extend(header.split())
    
    # Extract common business terms
    business_terms = re.findall(r'\b(action|jsp|struts|oracle|database|table|query|contract|policy|agreement|universal life|specified amount|document center)\b', content.lower())
    anchors.extend(business_terms)
    
    # Clean and deduplicate
    anchors = list(set([a.strip() for a in anchors if len(a.strip()) > 2]))
    
    return anchors

def add_business_glossary():
    """Add a business glossary document for better context."""
    
    glossary_content = """
# Legacy System Business Glossary

## Universal Life Insurance Terms

**Specified Amount**: The death benefit amount for a Universal Life insurance policy. Stored in agreement_values table with value_type 'DEATH BENEFIT AMOUNT'.

**Contract Options**: Configuration details for an insurance contract including plan name, insured person, issue age, premium class, etc.

**Agreement Values**: Database table (agreement_values) that stores various monetary values and settings for insurance agreements/contracts.

## Technical Terms

**Struts Action**: Java-based web action that handles HTTP requests. Actions are mapped to JSP pages for rendering.

**JSP (JavaServer Pages)**: Template files that generate dynamic web content. Often contain EL expressions like ${contractOptions.planName}.

**EL Expressions**: Expression Language syntax used in JSPs to access data objects, e.g., ${contractOptions.specifiedAmount}.

**Items and Expressions**: Security configuration that controls access to different parts of the application. Users get access through group and role assignments.

## Database Schemas

**IWDB**: Main application database containing user accounts, security settings, and application data.

**CPPF**: Contract/policy database containing agreement details, values, and policy-specific information.

## Key Tables

- **users**: User account information
- **agreement_values**: Contract values and settings  
- **ssc_groups, ssc_roles**: Security group and role definitions
- **ssc_group_items, ssc_role_items**: Item access mappings
- **items**: Available application features/functions
- **contextual_rules**: Dynamic access rules

## Common Access Patterns

**Static Items**: Items assigned to users through groups/roles (not contextual)
**Document Center**: Feature requiring SSC_COLI_Accounts and SSC_Client_Accounts_Business_Life_Documents_Menu items
**Summary Action**: Main policy/contract summary page at /iApp/ssc/clientAccounts/fixedLife/summary.action
"""
    
    doc = {
        "id": "business_glossary",
        "kind": "documentation", 
        "repo": "documentation",
        "path": "business_glossary.md",
        "sha": "latest",
        "source_env": "legacy",
        "anchors": [
            "glossary", "business terms", "universal life", "specified amount",
            "contract options", "agreement values", "struts", "jsp", "items",
            "expressions", "database", "iwdb", "cppf", "security", "access"
        ],
        "text": glossary_content
    }
    
    upsert(doc)
    print("Added business glossary")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Index documentation files")
    parser.add_argument("--docs-path", help="Path to documentation directory")
    parser.add_argument("--add-glossary", action="store_true", help="Add business glossary")
    
    args = parser.parse_args()
    
    if args.add_glossary:
        add_business_glossary()
    
    if args.docs_path:
        index_documentation(args.docs_path)
    
    if not args.docs_path and not args.add_glossary:
        print("Usage: python index_docs.py --docs-path /path/to/docs --add-glossary")
