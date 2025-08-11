#!/usr/bin/env python3
"""
Quick test script to verify the MVP is working correctly.
Run this after starting the containers to test the enhanced agent.
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_query(query: str, expected_keywords: list = None):
    """Test a single query and check response quality."""
    
    print(f"\n{'='*60}")
    print(f"TESTING: {query}")
    print('='*60)
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_BASE}/api/run",
            json={"query": query},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            print(response.text)
            return False
        
        result = response.json()
        duration = time.time() - start_time
        
        print(f"⏱️  Duration: {duration:.2f}s")
        print(f"📝 Answer Length: {len(result.get('final_answer', ''))} chars")
        print(f"🔗 Citations: {len(result.get('citations', []))}")
        print(f"👣 Steps: {len(result.get('steps', []))}")
        
        # Print answer
        print(f"\n📋 ANSWER:")
        print(result.get('final_answer', 'No answer'))
        
        # Print citations
        citations = result.get('citations', [])
        if citations:
            print(f"\n📚 CITATIONS:")
            for i, citation in enumerate(citations[:5], 1):
                print(f"  {i}. [{citation['type']}] {citation['path']}")
                if citation.get('content_preview'):
                    preview = citation['content_preview'][:100] + "..." if len(citation['content_preview']) > 100 else citation['content_preview']
                    print(f"     Preview: {preview}")
        
        # Print steps
        steps = result.get('steps', [])
        if steps:
            print(f"\n🏃 EXECUTION STEPS:")
            for step in steps:
                print(f"  • {step['step_name']}: {step['hit_count']} hits, {step['duration_ms']}ms")
        
        # Check for expected keywords
        if expected_keywords:
            answer_text = result.get('final_answer', '').lower()
            found_keywords = [kw for kw in expected_keywords if kw.lower() in answer_text]
            missing_keywords = [kw for kw in expected_keywords if kw.lower() not in answer_text]
            
            print(f"\n🔍 KEYWORD CHECK:")
            if found_keywords:
                print(f"  ✅ Found: {found_keywords}")
            if missing_keywords:
                print(f"  ❌ Missing: {missing_keywords}")
            
            success = len(found_keywords) >= len(expected_keywords) * 0.5  # At least 50% of keywords
        else:
            success = len(result.get('final_answer', '')) > 50  # At least some meaningful content
        
        print(f"\n{'✅ SUCCESS' if success else '❌ NEEDS IMPROVEMENT'}")
        return success
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_health():
    """Test basic health check."""
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def main():
    """Run all tests."""
    
    print("🚀 Testing Legacy Codebase Assistant MVP")
    print(f"API Base: {API_BASE}")
    
    # Health check
    if not test_health():
        print("❌ Cannot connect to API. Make sure containers are running.")
        return
    
    # Test queries based on golden questions
    test_cases = [
        {
            "query": "What query against IWDB will retrieve all the static Items associated with a given username from users table?",
            "expected": ["SELECT", "users", "ssc_group_users", "ssc_groups", "items", "contextual_rules"]
        },
        {
            "query": "Where does the 'Specified Amount' field get its data from on /iApp/ssc/clientAccounts/fixedLife/summary.action?",
            "expected": ["agreement_values", "DEATH BENEFIT AMOUNT", "database", "cppf"]
        },
        {
            "query": "What JSP contains the code that displays the Account Information for Universal Life contracts?",
            "expected": ["jsp", "loadedHeader", "WEB-INF", "fixedLife"]
        },
        {
            "query": "What are the possible data points for the contract options section of a UL contract?",
            "expected": ["contractOptions", "planName", "specifiedAmount", "benefits"]
        },
        {
            "query": "What Items and Expression combinations enable access to documentCenter.action?",
            "expected": ["SSC_COLI_Accounts", "SSC_Client_Accounts_Business_Life_Documents_Menu"]
        }
    ]
    
    # Run tests
    passed = 0
    total = len(test_cases)
    
    for test_case in test_cases:
        if test_query(test_case["query"], test_case["expected"]):
            passed += 1
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print(f"\n🏁 TEST SUMMARY")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed >= total * 0.8:
        print("🎉 MVP is working well!")
    elif passed >= total * 0.5:
        print("🔧 MVP working but needs tuning")
    else:
        print("🚨 MVP needs significant fixes")

if __name__ == "__main__":
    main()
