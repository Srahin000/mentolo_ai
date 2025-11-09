/**
 * Test script to verify frontend can query Cortex correctly
 * Run this in browser console or as a Node.js script
 */

const API_BASE_URL = 'http://localhost:3001/api';

async function testCortexAnalyze() {
  console.log('🧪 Testing Cortex Analyze Endpoint...\n');
  
  try {
    const response = await fetch(`${API_BASE_URL}/cortex/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        child_id: 'demo_child_tommy',
        analysis_type: 'trends',
        days: 90
      })
    });
    
    const data = await response.json();
    
    console.log('✅ Response Status:', response.status);
    console.log('📊 Response Data:', JSON.stringify(data, null, 2));
    
    if (data.available) {
      console.log('\n✅ Cortex is available and returning data');
      console.log('   Source:', data.source);
      console.log('   Analysis keys:', Object.keys(data.analysis || {}));
      
      if (data.analysis.trajectory) {
        console.log('   Trajectory:', data.analysis.trajectory);
      }
      if (data.analysis.strengths) {
        console.log('   Strengths count:', data.analysis.strengths.length);
      }
      if (data.analysis.growth_areas) {
        console.log('   Growth areas count:', data.analysis.growth_areas.length);
      }
    } else {
      console.log('\n⚠️  Cortex not available:', data.message);
      console.log('   Fallback:', data.fallback);
    }
    
    return data;
  } catch (error) {
    console.error('❌ Error:', error);
    throw error;
  }
}

async function testCortexQuery() {
  console.log('\n🧪 Testing Cortex Query Endpoint...\n');
  
  try {
    const response = await fetch(`${API_BASE_URL}/cortex/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        child_id: 'demo_child_tommy',
        question: 'What are the main trends in language development?'
      })
    });
    
    const data = await response.json();
    
    console.log('✅ Response Status:', response.status);
    console.log('📊 Response Data:', JSON.stringify(data, null, 2));
    
    if (data.available) {
      console.log('\n✅ Cortex Analyst is working');
      console.log('   Answer preview:', data.answer?.substring(0, 100) + '...');
    } else {
      console.log('\n⚠️  Cortex Analyst not available:', data.message);
    }
    
    return data;
  } catch (error) {
    console.error('❌ Error:', error);
    throw error;
  }
}

// Run tests
(async () => {
  console.log('='.repeat(70));
  console.log('Frontend Cortex API Test');
  console.log('='.repeat(70));
  
  await testCortexAnalyze();
  await testCortexQuery();
  
  console.log('\n' + '='.repeat(70));
  console.log('Test Complete');
  console.log('='.repeat(70));
})();

