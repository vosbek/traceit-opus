# 🚀 Legacy Codebase Assistant MVP - Quick Start Guide

## What's Been Fixed & Enhanced

✅ **Real Strands Agent Implementation** - Multi-step reasoning with proper tool orchestration  
✅ **Enhanced Oracle Tool** - Better SQL validation with safety checks  
✅ **Neo4j Graph Integration** - Struts/JSP mapping support  
✅ **Multi-Source Evidence** - Combines code, database, and documentation  
✅ **Quality Citations** - Proper evidence linking and source attribution  
✅ **Step Tracing** - Full execution visibility for debugging  

## Quick Start (2-Day MVP)

### 1. Start the Containers
```bash
cd C:\devl\workspaces\trace-strands-opus
podman-compose -f compose/podman-compose.yml up -d
```

### 2. Setup Sample Data
```bash
# Wait for containers to be healthy (check with docker ps)
# Then run setup
python setup_mvp.py
```

### 3. Add Business Documentation (Optional)
```bash
# Add business glossary
python index_docs.py --add-glossary

# Index your documentation directory
python index_docs.py --docs-path /path/to/your/docs
```

### 4. Test the MVP
```bash
python test_mvp.py
```

### 5. Access the UI
- API: http://localhost:8000
- UI: http://localhost:4200  
- Neo4j Browser: http://localhost:7474 (neo4j/test)

## Example Queries to Test

1. **Database Query**: "Where does 'Specified Amount' come from on the summary action?"
2. **JSP Mapping**: "What JSP contains the Account Information for Universal Life?"
3. **Security Items**: "What Items enable access to documentCenter.action?"
4. **Contract Options**: "What data points appear in contract options for UL?"

## Architecture Overview

```
Query → Agent → [Analyze] → [Search Code] → [Query DB] → [Synthesize] → Answer
                     ↓           ↓            ↓           ↓
                 Query Type   OpenSearch   Oracle DB   Citations + 
                 Analysis    + Neo4j       Read-Only   Evidence
```

## Key Improvements Made

### 1. **Enhanced Agent Orchestration**
- **Before**: Single search step, basic formatting
- **After**: 4-step process with query analysis, multi-source search, database verification, synthesis

### 2. **Proper Tool Integration**  
- **Before**: Tools defined but never used
- **After**: Tools actively called by agent with proper error handling

### 3. **Better SQL Safety**
- **Before**: Naive string check easily bypassed
- **After**: Multiple validation layers + automatic row limiting

### 4. **Multi-Source Evidence**
- **Before**: Only code search
- **After**: Code + Database + Neo4j + Documentation

### 5. **Quality Citations**
- **Before**: Hard-coded citation format
- **After**: Evidence-based citations with content previews

## Configuration

### Environment Variables (.env file)
```bash
# Oracle Database
ORACLE_DSN=your_oracle_dsn
ORACLE_USER=your_oracle_user
ORACLE_PASS=your_oracle_password

# OpenSearch
OPENSEARCH_URL=http://opensearch:9200
OS_INDEX=traceit_docs

# Neo4j
NEO4J_URL=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASS=test
```

## Adding Your Real Data

### 1. **Index Your Codebases**
```bash
# Create repos.csv with your repository paths
echo "repo" > config/repos.csv
echo "/path/to/your/legacy/repo1" >> config/repos.csv
echo "/path/to/your/legacy/repo2" >> config/repos.csv

# Run indexing
python -m indexers.run --repos config/repos.csv
```

### 2. **Update Oracle Connection**
- Set your real Oracle credentials in `.env`
- Test connection with simple query

### 3. **Build Real Neo4j Relationships**
- Extend `setup_mvp.py` with your actual Struts configs
- Add real JSP→Action mappings from your codebase

### 4. **Add Documentation**
- Use `index_docs.py` to add your business docs
- Update business glossary with your terminology

## Troubleshooting

### Common Issues

**Agent not using tools properly**
- Check Strands SDK installation: `pip show strands-agents`
- Verify tool imports in orchestrators/answer_agent.py

**No database results**
- Verify Oracle credentials in .env
- Check network connectivity to Oracle
- Test with simple SELECT 1 FROM dual

**Poor search results**
- Run indexing on your actual codebases
- Add more sample documents with `index_docs.py`
- Check OpenSearch at http://localhost:9200/_cat/indices

**No Neo4j relationships**
- Access Neo4j browser: http://localhost:7474
- Run: `MATCH (n) RETURN count(n)` to check data
- Re-run `setup_mvp.py` if needed

### Performance Tuning

**Slow queries (>15 seconds)**
- Reduce OpenSearch result size in retrievers/pipeline.py
- Add database query timeouts
- Consider caching frequent queries

**Poor answer quality**
- Add more business context documents
- Improve query analysis patterns in answer_agent.py
- Tune evidence thresholds

## Next Steps for Production

### Week 1 Enhancements
1. **Real Data Integration**
   - Index your full codebases
   - Build comprehensive Neo4j graph
   - Add all business documentation

2. **Query Optimization**
   - Add query caching
   - Improve SQL generation patterns
   - Enhanced error handling

### Week 2 Features
1. **Conversation Memory**
   - Multi-turn conversations
   - Follow-up question support
   - Context preservation

2. **Advanced Tools**
   - diff_analyzer for legacy vs target comparison
   - CODEOWNERS integration
   - Dependency analysis

### Production Readiness
1. **Security**
   - Proper SQL injection prevention
   - Input validation
   - Audit logging

2. **Monitoring**
   - Query analytics
   - Performance metrics
   - Error tracking

3. **Scalability**
   - Connection pooling
   - Caching layer
   - Load balancing

## Contact & Support

This MVP gives you a solid foundation for the "talk to codebase" concept with proper Strands integration. The multi-step reasoning and evidence combination should provide much higher quality answers than the original implementation.

Focus on getting real data indexed first, then iterate on query patterns and answer quality based on your team's actual questions.
