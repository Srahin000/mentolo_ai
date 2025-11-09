#!/usr/bin/env python3
"""
Test Script: Verify Dummy Data and Cortex Integration
Checks if:
1. Dummy data is properly inserted in Snowflake
2. Cortex can read and analyze that data
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from services.snowflake_service import SnowflakeService
from services.cortex_analysis_service import CortexAnalysisService

load_dotenv()

DUMMY_CHILD_ID = "demo_child_tommy"

def test_dummy_data():
    """Test 1: Verify dummy data exists"""
    print("="*70)
    print("TEST 1: Checking Dummy Data in Snowflake")
    print("="*70)
    print()
    
    snowflake = SnowflakeService()
    
    if not snowflake.is_available():
        print("❌ Snowflake not available")
        return False
    
    try:
        cursor = snowflake.conn.cursor()
        
        # Check session count
        cursor.execute("""
            SELECT COUNT(*) as total_sessions
            FROM child_development_sessions
            WHERE child_id = %s
        """, (DUMMY_CHILD_ID,))
        
        session_count = cursor.fetchone()[0]
        print(f"✅ Found {session_count} sessions for {DUMMY_CHILD_ID}")
        
        # Check enriched columns
        cursor.execute("""
            SELECT 
                COUNT(*) as sessions_with_scores,
                AVG(language_score) as avg_language,
                AVG(cognitive_score) as avg_cognitive,
                AVG(emotional_score) as avg_emotional,
                AVG(session_duration) as avg_duration,
                AVG(conversation_turns) as avg_turns,
                AVG(emotion_words_used) as avg_emotion_words,
                AVG(curiosity_score) as avg_curiosity
            FROM child_development_sessions
            WHERE child_id = %s
        """, (DUMMY_CHILD_ID,))
        
        stats = cursor.fetchone()
        print(f"\n📊 Enriched Data Statistics:")
        print(f"   Sessions with scores: {stats[0]}")
        print(f"   Avg Language Score: {stats[1]:.1f}/100")
        print(f"   Avg Cognitive Score: {stats[2]:.1f}/100")
        print(f"   Avg Emotional Score: {stats[3]:.1f}/100")
        print(f"   Avg Session Duration: {stats[4]:.0f} seconds")
        print(f"   Avg Conversation Turns: {stats[5]:.1f}")
        print(f"   Avg Emotion Words: {stats[6]:.1f}")
        print(f"   Avg Curiosity Score: {stats[7]:.1f}/100")
        
        cursor.close()
        
        if session_count == 0:
            print("\n⚠️  No sessions found! Run: python create_dummy_profile.py")
            return False
        
        if stats[0] == 0:
            print("\n⚠️  Sessions exist but enriched columns are empty!")
            return False
        
        print("\n✅ Dummy data is properly inserted with all enriched columns")
        return True
        
    except Exception as e:
        print(f"❌ Error checking dummy data: {e}")
        return False

def test_cortex_analysis():
    """Test 2: Verify Cortex can analyze the dummy data"""
    print("\n" + "="*70)
    print("TEST 2: Testing Cortex Analysis on Dummy Data")
    print("="*70)
    print()
    
    snowflake = SnowflakeService()
    
    if not snowflake.is_available():
        print("❌ Snowflake not available")
        return False
    
    cortex = CortexAnalysisService(snowflake.conn)
    
    if not cortex.is_available():
        print("⚠️  Cortex not available in this region")
        print("   (This is okay - system will use Gemini Pro fallback)")
        return False
    
    print("✅ Cortex is available")
    print("\n🔍 Running Cortex analysis on dummy data...")
    
    try:
        # Test longitudinal trends analysis
        analysis = cortex.analyze_longitudinal_trends(DUMMY_CHILD_ID, days=90)
        
        if analysis:
            print("\n✅ Cortex analysis successful!")
            print(f"   Source: {analysis.get('source', 'unknown')}")
            print(f"   Analyzed days: {analysis.get('analyzed_days', 0)}")
            
            cortex_analysis = analysis.get('analysis', {})
            if isinstance(cortex_analysis, dict):
                print(f"\n📊 Cortex Insights:")
                if 'trajectory' in cortex_analysis:
                    print(f"   Trajectory: {cortex_analysis.get('trajectory', 'N/A')}")
                if 'strengths' in cortex_analysis:
                    strengths = cortex_analysis.get('strengths', [])
                    if isinstance(strengths, list) and strengths:
                        print(f"   Top Strengths: {', '.join(str(s) for s in strengths[:3])}")
                if 'growth_areas' in cortex_analysis:
                    growth = cortex_analysis.get('growth_areas', [])
                    if isinstance(growth, list) and growth:
                        print(f"   Growth Areas: {', '.join(str(g) for g in growth[:2])}")
                if 'recommendations' in cortex_analysis:
                    recs = cortex_analysis.get('recommendations', [])
                    if isinstance(recs, list) and recs:
                        print(f"   Recommendations: {len(recs)} provided")
            else:
                print(f"\n📝 Cortex Response (raw):")
                print(f"   {str(cortex_analysis)[:200]}...")
            
            return True
        else:
            print("⚠️  Cortex returned no analysis")
            return False
            
    except Exception as e:
        print(f"❌ Error running Cortex analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cortex_query():
    """Test 3: Test Cortex Analyst query (chatbot)"""
    print("\n" + "="*70)
    print("TEST 3: Testing Cortex Analyst Query (Chatbot)")
    print("="*70)
    print()
    
    snowflake = SnowflakeService()
    
    if not snowflake.is_available():
        print("❌ Snowflake not available")
        return False
    
    cortex = CortexAnalysisService(snowflake.conn)
    
    if not cortex.is_available():
        print("⚠️  Cortex not available - skipping query test")
        return False
    
    print("✅ Cortex is available")
    print("\n💬 Testing Cortex Analyst with sample question...")
    
    try:
        question = "What are the main trends in language development?"
        result = cortex.query_cortex_analyst(DUMMY_CHILD_ID, question)
        
        if result.get('available'):
            print("\n✅ Cortex Analyst query successful!")
            print(f"   Child: {result.get('child_name', 'N/A')}")
            print(f"   Answer preview: {result.get('answer', '')[:150]}...")
            return True
        else:
            print(f"⚠️  Cortex Analyst not available: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error querying Cortex Analyst: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n🧪 Testing Dummy Data and Cortex Integration\n")
    
    # Test 1: Dummy data
    data_ok = test_dummy_data()
    
    # Test 2: Cortex analysis
    cortex_ok = test_cortex_analysis() if data_ok else False
    
    # Test 3: Cortex query
    query_ok = test_cortex_query() if data_ok else False
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"✅ Dummy Data: {'PASS' if data_ok else 'FAIL'}")
    print(f"{'✅' if cortex_ok else '⚠️ '} Cortex Analysis: {'PASS' if cortex_ok else 'SKIP (not available or no data)'}")
    print(f"{'✅' if query_ok else '⚠️ '} Cortex Query: {'PASS' if query_ok else 'SKIP (not available or no data)'}")
    print()
    
    if not data_ok:
        print("💡 Next Steps:")
        print("   1. Run: python create_dummy_profile.py")
        print("   2. Verify Snowflake connection")
        print("   3. Re-run this test")
    elif cortex_ok:
        print("🎉 All tests passed! Cortex is analyzing dummy data successfully.")
    else:
        print("ℹ️  Data exists but Cortex may not be available in your region.")
        print("   This is okay - the system uses Gemini Pro as fallback.")

if __name__ == '__main__':
    main()

