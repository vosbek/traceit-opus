
        query = m.metadata.get("original_query", "")
        
        # Use Bedrock SQL agent
        db_results = bedrock_sql_query(query)
        
        return Message(
            role="assistant",
            content=f"Database query executed: {db_results.get('row_count', 0)} rows",
            metadata={
                **m.metadata,
                "db_results": db_results,
                "sql_executed": db_results.get("generated_sql", ""),
                "sql_explanation": db_results.get("sql_explanation", "")
            }
        )
    
    @step
    def search_documentation(self, m: Message) -> Message:
        """
        Search indexed documentation with semantic understanding.
        """
        query = m.metadata.get("original_query", "")
        
        # Search documentation
        doc_results = self.search_docs_semantic(query)
        
        # Extract relevant sections
        relevant_sections = []
        for doc in doc_results[:5]:
            if doc.get("summary"):
                relevant_sections.append({
                    "source": doc.get("file_name", ""),
                    "summary": doc.get("summary", ""),
                    "business_rules": doc.get("business_rules", [])
                })
        
        return Message(
            role="assistant",
            content=f"Found {len(doc_results)} documentation matches",
            metadata={
                **m.metadata,
                "doc_results": doc_results,
                "relevant_sections": relevant_sections
            }
        )
    
    @step
    def check_corba_interfaces(self, m: Message) -> Message:
        """
        Check CORBA interfaces if relevant.
        """
        query = m.metadata.get("original_query", "")
        
        if not any(word in query.lower() for word in ["service", "interface", "corba", "remote"]):
            return Message(
                role="assistant",
                content="CORBA check not needed",
                metadata=m.metadata
            )
        
        # Search CORBA interfaces
        corba_results = self.search_corba_interfaces(query)
        
        return Message(
            role="assistant",
            content=f"Found {len(corba_results)} CORBA interfaces",
            metadata={
                **m.metadata,
                "corba_results": corba_results
            }
        )
    
    @step
    def synthesize_comprehensive_answer(self, m: Message) -> Message:
        """
        Final synthesis using Bedrock with all evidence.
        """
        # Gather all evidence
        evidence = {
            "code_hits": m.metadata.get("code_hits", []),
            "jar_results": m.metadata.get("jar_results", []),
            "business_rules": m.metadata.get("business_rules", []),
            "db_results": m.metadata.get("db_results", {}),
            "doc_results": m.metadata.get("doc_results", []),
            "corba_results": m.metadata.get("corba_results", [])
        }
        
        # Use Bedrock to synthesize
        final_answer = self.synthesize_with_bedrock(
            m.metadata.get("original_query", ""),
            evidence
        )
        
        # Record metrics
        self.update_metrics(m.metadata)
        
        # Generate query ID for feedback
        import hashlib
        query_id = hashlib.md5(m.metadata.get("original_query", "").encode()).hexdigest()
        
        return Message(
            role="assistant",
            content=final_answer["answer"],
            metadata={
                "final_answer": final_answer["answer"],
                "citations": final_answer["citations"],
                "confidence": final_answer["confidence"],
                "query_id": query_id,
                "execution_time": time.time() - m.metadata.get("start_time", time.time()),
                "evidence_sources": list(set([c["type"] for c in final_answer["citations"]]))
            }
        )
    
    def analyze_intent_with_bedrock(self, query: str) -> Dict[str, Any]:
        """
        Use Bedrock to deeply understand query intent.
        """
        prompt = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": f"""Analyze this developer query about a legacy insurance system:

Query: {query}

Identify:
1. Primary intent (what they're trying to find/solve)
2. Technical domain (UI, database, business logic, integration)
3. Urgency indicators (debugging, migration, understanding)
4. Key entities mentioned (tables, classes, methods, files)
5. Expected answer format (code location, explanation, list, etc.)

Return in JSON format."""
                }
            ]
        }
        
        try:
            response = self.bedrock.invoke_model(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                body=json.dumps(prompt)
            )
            
            result = json.loads(response['body'].read())
            intent = json.loads(result['content'][0]['text'])
            return {"intent_analysis": intent}
            
        except Exception as e:
            print(f"Error analyzing intent: {e}")
            return {"intent_analysis": {}}
    
    def extract_search_terms(self, query: str) -> List[str]:
        """
        Extract optimal search terms from query.
        """
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'what', 'where', 'when', 'how', 'why',
                     'does', 'do', 'is', 'are', 'was', 'were', 'been', 'being', 'have',
                     'has', 'had', 'will', 'would', 'could', 'should', 'may', 'might'}
        
        words = query.lower().split()
        terms = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Add combinations for better matching
        if len(terms) >= 2:
            terms.append(' '.join(terms[:2]))
        
        return terms
    
    def create_execution_plan(self, optimizations: Dict, intent: Dict) -> List[str]:
        """
        Create optimal execution plan based on analysis.
        """
        plan = []
        
        query_type = optimizations.get("query_type", "general")
        suggested_tools = optimizations.get("suggested_tools", [])
        
        # Prioritize tools based on query type
        if "bedrock_sql_query" in suggested_tools and "database" in query_type:
            plan.append("query_database_smart")
        
        plan.append("search_codebase_enhanced")
        
        if "business_logic" in query_type:
            plan.append("search_jars_if_needed")
        
        if "documentation_search" in suggested_tools:
            plan.append("search_documentation")
        
        if "corba" in optimizations.get("original_query", "").lower():
            plan.append("check_corba_interfaces")
        
        plan.append("synthesize_comprehensive_answer")
        
        return plan
    
    def search_with_context(self, term: str, analysis: Dict) -> List[Dict]:
        """
        Search with codebase-specific context.
        """
        # Build OpenSearch query with boosts
        query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": term,
                                "fields": ["text^2", "anchors", "search_text"],
                                "type": "best_fields"
                            }
                        }
                    ],
                    "should": []
                }
            },
            "size": 20
        }
        
        # Add boosts based on query type
        query_type = analysis.get("query_type", "")
        if "ui_related" in query_type:
            query["query"]["bool"]["should"].append({
                "match": {"path": {"query": ".jsp", "boost": 2}}
            })
        elif "api_related" in query_type:
            query["query"]["bool"]["should"].append({
                "match": {"annotations": {"query": "Controller", "boost": 2}}
            })
        
        try:
            results = self.os_client.search(
                index="legacy_code,legacy_jars",
                body=query
            )
            
            hits = []
            for hit in results['hits']['hits']:
                hits.append({
                    "id": hit['_id'],
                    "score": hit['_score'],
                    **hit['_source']
                })
            
            return hits
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def search_jar_contents(self, query: str) -> List[Dict]:
        """
        Search indexed JAR contents.
        """
        query_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["search_text", "methods", "annotations", "business_rules"],
                    "type": "best_fields"
                }
            },
            "size": 10
        }
        
        try:
            results = self.os_client.search(
                index="legacy_jars",
                body=query_body
            )
            
            return [hit['_source'] for hit in results['hits']['hits']]
            
        except Exception as e:
            print(f"JAR search error: {e}")
            return []
    
    def search_docs_semantic(self, query: str) -> List[Dict]:
        """
        Semantic search in documentation.
        """
        query_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "summary^2", "text", "topics", "glossary"],
                    "type": "best_fields"
                }
            },
            "size": 10
        }
        
        try:
            results = self.os_client.search(
                index="legacy_documentation",
                body=query_body
            )
            
            return [hit['_source'] for hit in results['hits']['hits']]
            
        except Exception as e:
            print(f"Documentation search error: {e}")
            return []
    
    def search_corba_interfaces(self, query: str) -> List[Dict]:
        """
        Search CORBA interfaces.
        """
        query_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["interfaces", "operations", "search_text"],
                    "type": "best_fields"
                }
            },
            "size": 10
        }
        
        try:
            results = self.os_client.search(
                index="legacy_corba",
                body=query_body
            )
            
            return [hit['_source'] for hit in results['hits']['hits']]
            
        except Exception as e:
            print(f"CORBA search error: {e}")
            return []
    
    def rank_results(self, hits: List[Dict], analysis: Dict) -> List[Dict]:
        """
        Rank results based on learned patterns and relevance.
        """
        # Apply scoring based on patterns
        for hit in hits:
            score = hit.get("score", 0)
            
            # Boost based on query type match
            if analysis.get("query_type") == "ui_related" and ".jsp" in hit.get("path", ""):
                score *= 1.5
            elif analysis.get("query_type") == "api_related" and "Controller" in hit.get("class_name", ""):
                score *= 1.5
            
            # Boost if matches business terms
            if self.pattern_learner.patterns.get("business_terms"):
                for term in self.pattern_learner.patterns["business_terms"]:
                    if term in hit.get("text", ""):
                        score *= 1.2
                        break
            
            hit["adjusted_score"] = score
        
        # Sort by adjusted score
        return sorted(hits, key=lambda x: x.get("adjusted_score", 0), reverse=True)
    
    def synthesize_with_bedrock(self, query: str, evidence: Dict) -> Dict[str, Any]:
        """
        Use Bedrock to create final answer from all evidence.
        """
        # Prepare evidence summary
        evidence_text = self.format_evidence(evidence)
        
        prompt = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 3000,
            "messages": [
                {
                    "role": "user",
                    "content": f"""You are helping a developer understand a legacy insurance system.

Question: {query}

Evidence gathered:
{evidence_text}

Provide a comprehensive answer that:
1. Directly answers the question
2. Cites specific files, classes, tables, or documentation
3. Explains the business logic or technical implementation
4. Notes any important caveats or assumptions
5. Suggests next steps or related areas to investigate

Format the answer for a developer who needs actionable information."""
                }
            ]
        }
        
        try:
            response = self.bedrock.invoke_model(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                body=json.dumps(prompt)
            )
            
            result = json.loads(response['body'].read())
            answer = result['content'][0]['text']
            
            # Extract citations
            citations = self.extract_citations_from_answer(answer, evidence)
            
            # Estimate confidence
            confidence = self.estimate_confidence(evidence, citations)
            
            return {
                "answer": answer,
                "citations": citations,
                "confidence": confidence
            }
            
        except Exception as e:
            print(f"Error synthesizing answer: {e}")
            return {
                "answer": "Error generating answer. Please try again.",
                "citations": [],
                "confidence": 0
            }
    
    def format_evidence(self, evidence: Dict) -> str:
        """
        Format evidence for Bedrock prompt.
        """
        lines = []
        
        if evidence.get("code_hits"):
            lines.append("CODE EVIDENCE:")
            for hit in evidence["code_hits"][:5]:
                lines.append(f"- {hit.get('path', 'unknown')}: {hit.get('text', '')[:200]}")
        
        if evidence.get("jar_results"):
            lines.append("\nJAR/CLASS EVIDENCE:")
            for result in evidence["jar_results"][:3]:
                lines.append(f"- {result.get('class_name', 'unknown')}: {result.get('methods', [])[:5]}")
        
        if evidence.get("business_rules"):
            lines.append("\nBUSINESS RULES:")
            for rule in evidence["business_rules"][:5]:
                lines.append(f"- {rule.get('description', '')}")
        
        if evidence.get("db_results", {}).get("rows"):
            lines.append("\nDATABASE EVIDENCE:")
            lines.append(f"- Query: {evidence['db_results'].get('generated_sql', '')}")
            lines.append(f"- Results: {evidence['db_results'].get('row_count', 0)} rows")
        
        if evidence.get("doc_results"):
            lines.append("\nDOCUMENTATION:")
            for doc in evidence["doc_results"][:3]:
                lines.append(f"- {doc.get('title', '')}: {doc.get('summary', '')[:200]}")
        
        return "\n".join(lines)
    
    def extract_citations_from_answer(self, answer: str, evidence: Dict) -> List[Dict]:
        """
        Extract citations from the generated answer.
        """
        citations = []
        
        # Check for code file references
        import re
        file_patterns = re.findall(r'[\w/]+\.(?:java|jsp|xml|properties)', answer)
        for pattern in file_patterns:
            citations.append({
                "type": "code",
                "reference": pattern
            })
        
        # Check for table references
        table_patterns = re.findall(r'\b(?:table|from)\s+(\w+)', answer, re.IGNORECASE)
        for table in table_patterns:
            citations.append({
                "type": "database",
                "reference": table
            })
        
        # Check for class references
        class_patterns = re.findall(r'\b[A-Z][a-zA-Z]*(?:Controller|Service|DAO|Manager)\b', answer)
        for class_name in class_patterns:
            citations.append({
                "type": "class",
                "reference": class_name
            })
        
        return citations
    
    def estimate_confidence(self, evidence: Dict, citations: List) -> float:
        """
        Estimate confidence in the answer.
        """
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on evidence
        if evidence.get("code_hits"):
            confidence += 0.15
        if evidence.get("db_results", {}).get("rows"):
            confidence += 0.15
        if evidence.get("doc_results"):
            confidence += 0.1
        if evidence.get("business_rules"):
            confidence += 0.1
        
        # Adjust based on citations
        if len(citations) > 3:
            confidence += 0.1
        
        return min(confidence, 0.95)  # Cap at 95%
    
    def update_metrics(self, metadata: Dict):
        """
        Update execution metrics for monitoring.
        """
        self.metrics["queries_processed"] += 1
        
        # Update average response time
        exec_time = metadata.get("execution_time", 0)
        avg = self.metrics["avg_response_time"]
        count = self.metrics["queries_processed"]
        self.metrics["avg_response_time"] = (avg * (count - 1) + exec_time) / count
        
        # Track tool usage
        for tool in ["code_hits", "db_results", "doc_results", "jar_results"]:
            if metadata.get(tool):
                self.metrics["tool_usage"][tool] = self.metrics["tool_usage"].get(tool, 0) + 1


# Create the enhanced plan
enhanced_plan = Plan()\
    .add("analyze_and_optimize_query")\
    .add("search_codebase_enhanced")\
    .add("search_jars_if_needed")\
    .add("query_database_smart")\
    .add("search_documentation")\
    .add("check_corba_interfaces")\
    .add("synthesize_comprehensive_answer")
