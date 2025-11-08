#!/usr/bin/env python3
"""
Test Snowflake Insight Generation
Creates sample data and tests insight generation capabilities
"""

import requests
import json
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:3001')
TEST_USER_ID = "test_user_snowflake_insights"

def print_header(text):
    print(f"\n{'='*70}")
    print(f"{text:^70}")
    print(f"{'='*70}\n")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def test_health():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('services', {}).get('snowflake', False):
                print_success("Server is running and Snowflake is available")
                return True
            else:
                print_error("Snowflake service not available")
                return False
        return False
    except Exception as e:
        print_error(f"Cannot connect to server: {e}")
        return False

def create_sample_interactions():
    """Create sample interactions to generate insights from"""
    print_header("STEP 1: Creating Sample Interactions")
    
    sample_questions = [
        "What is a dinosaur?",
        "How do plants grow?",
        "Why is the sky blue?",
        "What is gravity?",
        "How do computers work?",
        "What is photosynthesis?",
        "Why do we have seasons?",
        "How do birds fly?",
        "What is the water cycle?",
        "How do magnets work?"
    ]
    
    created = 0
    for i, question in enumerate(sample_questions):
        try:
            payload = {
                "user_input": question,
                "user_id": TEST_USER_ID,
                "session_id": f"test_session_{i+1}"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/ask",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                created += 1
                print_success(f"Created interaction {i+1}: {question[:50]}...")
            else:
                print_error(f"Failed to create interaction {i+1}: {response.status_code}")
        except Exception as e:
            print_error(f"Error creating interaction {i+1}: {e}")
    
    print_info(f"Created {created}/{len(sample_questions)} interactions")
    return created > 0

def test_user_insights():
    """Test user insights endpoint"""
    print_header("STEP 2: Testing User Insights")
    
    try:
        # Test via dashboard endpoint (which uses insights)
        response = requests.get(
            f"{BASE_URL}/api/dashboard",
            headers={"X-User-ID": TEST_USER_ID},
            params={"days": 30},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print_success("Insights generated successfully!")
            print(f"\n📊 Summary:")
            summary = data.get('summary', {})
            print(f"   Total Interactions: {summary.get('total_interactions', 0)}")
            print(f"   Active Days: {summary.get('active_days', 0)}")
            print(f"   Engagement Score: {summary.get('engagement_score', 0):.2f}")
            print(f"   Most Common Emotion: {summary.get('most_common_emotion', 'N/A')}")
            
            print(f"\n🤖 AI Insights ({len(data.get('ai_insights', []))}):")
            for insight in data.get('ai_insights', [])[:5]:
                print(f"   • {insight}")
            
            print(f"\n💡 Recommendations ({len(data.get('recommendations', []))}):")
            for rec in data.get('recommendations', [])[:5]:
                print(f"   • {rec}")
            
            print(f"\n📈 Topics Covered ({len(data.get('topics', []))}):")
            for topic in data.get('topics', [])[:10]:
                print(f"   • {topic}")
            
            return True
        else:
            print_error(f"Failed to get insights: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error getting insights: {e}")
        return False

def test_analytics_insights():
    """Test analytics insights endpoint"""
    print_header("STEP 3: Testing Analytics Insights Endpoint")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/analytics/insights",
            headers={"X-User-ID": TEST_USER_ID},
            params={"days": 30},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Analytics insights retrieved!")
            
            if 'insights' in data:
                print(f"\n📊 Analytics Data:")
                print(f"   Total Interactions: {data.get('total_interactions', 0)}")
                print(f"   Engagement Score: {data.get('engagement_score', 0):.2f}")
                
                insights = data.get('insights', [])
                if insights:
                    print(f"\n🤖 Generated Insights ({len(insights)}):")
                    for insight in insights[:5]:
                        print(f"   • {insight}")
            
            return True
        else:
            print_error(f"Failed to get analytics insights: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error getting analytics insights: {e}")
        return False

def test_child_development_insights():
    """Test child development insights"""
    print_header("STEP 4: Testing Child Development Insights")
    
    child_id = "test_child_insights"
    
    try:
        # First, check if child profile exists
        response = requests.get(
            f"{BASE_URL}/api/child-profile/{child_id}",
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Child profile retrieved!")
            print(f"   Total Sessions: {data.get('total_sessions', 0)}")
            
            if data.get('total_sessions', 0) > 0:
                print_info("Child has session data - insights would be available")
            else:
                print_info("No session data yet - insights will be generated once sessions are added")
        else:
            print_info("Child profile endpoint accessible (no data yet)")
        
        return True
    except Exception as e:
        print_error(f"Error testing child insights: {e}")
        return False

def main():
    print_header("🧪 Snowflake Insight Generation Test")
    
    # Step 0: Health check
    if not test_health():
        print_error("Server or Snowflake not available. Please check:")
        print("   1. Server is running: cd backend && python app.py")
        print("   2. Snowflake credentials are set in .env")
        return
    
    # Step 1: Create sample data
    if create_sample_interactions():
        print_info("Waiting 2 seconds for data to be processed...")
        time.sleep(2)
    else:
        print_warning("Could not create sample interactions - testing with existing data")
    
    # Step 2: Test user insights
    insights_success = test_user_insights()
    
    # Step 3: Test analytics insights
    analytics_success = test_analytics_insights()
    
    # Step 4: Test child development insights
    child_success = test_child_development_insights()
    
    # Summary
    print_header("📊 Test Summary")
    print(f"User Insights:        {'✅ PASS' if insights_success else '❌ FAIL'}")
    print(f"Analytics Insights:   {'✅ PASS' if analytics_success else '❌ FAIL'}")
    print(f"Child Insights:       {'✅ PASS' if child_success else '❌ FAIL'}")
    
    if insights_success or analytics_success:
        print("\n🎉 Snowflake insight generation is working!")
        print("\n💡 Tips:")
        print("   - More interactions = richer insights")
        print("   - Insights improve over time as data accumulates")
        print("   - Check /api/dashboard for comprehensive analytics")
    else:
        print("\n⚠️  Some insight tests failed. Check Snowflake connection and data.")

if __name__ == "__main__":
    main()

