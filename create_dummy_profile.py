#!/usr/bin/env python3
"""
Create Enriched Dummy Child Profile in Snowflake
Generates 3 months of realistic child development data with enriched analytics
"""

import os
import sys
import json
import uuid
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from dotenv import load_dotenv
from services.snowflake_service import SnowflakeService

load_dotenv()

# Dummy child profile data
DUMMY_CHILD_ID = "demo_child_tommy"
CHILD_NAME = "Tommy"
CHILD_AGE = 5

# Conversation templates for realistic transcripts
CONVERSATION_TEMPLATES = [
    ("dinosaurs", [
        f"Parent: How was your day at school today?",
        f"{CHILD_NAME}: It was good! We learned about dinosaurs. Did you know that T-Rex had really big teeth?",
        f"Parent: Wow, that's interesting! What else did you learn?",
        f"{CHILD_NAME}: The teacher said they lived a long, long time ago. I wonder what it would be like to see one?",
        f"Parent: That's a great question! What do you think?",
        f"{CHILD_NAME}: I think it would be scary but also really cool. Maybe we could read a book about it?"
    ]),
    ("space", [
        f"Parent: What did you do today?",
        f"{CHILD_NAME}: I drew a picture of a rocket ship! It goes really fast to the moon.",
        f"Parent: That sounds amazing! Tell me more about your rocket.",
        f"{CHILD_NAME}: It has big engines and can carry astronauts. I want to be an astronaut when I grow up!",
        f"Parent: That's a wonderful dream! What would you do in space?",
        f"{CHILD_NAME}: I would float around and see all the stars. There are so many!"
    ]),
    ("building", [
        f"Parent: What are you building with your blocks?",
        f"{CHILD_NAME}: I'm making a tall tower! Watch, it's getting really high.",
        f"Parent: That's impressive! How many blocks did you use?",
        f"{CHILD_NAME}: I think maybe twenty? Let me count... one, two, three...",
        f"Parent: Great counting! What will you build next?",
        f"{CHILD_NAME}: Maybe a bridge! Bridges help people cross over water."
    ]),
    ("storytelling", [
        f"Parent: Can you tell me a story?",
        f"{CHILD_NAME}: Once upon a time, there was a brave knight who saved a princess from a dragon!",
        f"Parent: That's exciting! What happened next?",
        f"{CHILD_NAME}: The knight had a magic sword and the dragon was actually friendly. They became friends!",
        f"Parent: I love that ending! What was the princess's name?",
        f"{CHILD_NAME}: Her name was... um... Princess Sparkle! She had a magic crown."
    ]),
    ("animals", [
        f"Parent: What's your favorite animal?",
        f"{CHILD_NAME}: I love elephants! They're so big and have long trunks.",
        f"Parent: Why do you like elephants?",
        f"{CHILD_NAME}: Because they're gentle and they remember things. The teacher said they're really smart!",
        f"Parent: That's true! What else do you know about elephants?",
        f"{CHILD_NAME}: They live in families and the mommy elephants take care of the babies. Just like you take care of me!"
    ])
]

STRENGTHS_POOL = [
    "Storytelling Genius",
    "Question Asker Extraordinaire",
    "Empathy Star",
    "Creative Problem Solver",
    "Curious Explorer",
    "Social Connector",
    "Imaginative Thinker"
]

GROWTH_AREAS_POOL = [
    "Number Recognition",
    "Time Concepts",
    "Following Multi-Step Instructions",
    "Emotional Regulation",
    "Fine Motor Skills",
    "Pattern Recognition"
]

ACTIVITIES_POOL = [
    "Read a 'why' book together",
    "Play 'I Spy' with describing words",
    "Ask {CHILD_NAME} to retell a favorite story",
    "Build something together with blocks",
    "Draw a picture and tell a story about it",
    "Practice counting with everyday objects",
    "Play a pretend game together"
]

def create_enriched_analysis(session_num, total_sessions, days_ago):
    """Generate enriched analysis data with all new fields"""
    
    # Progress increases over time with some variation
    progress_factor = min(1.0, session_num / total_sessions)
    
    # Each score type has its own base, growth rate, and variation pattern
    # This makes them look different and realistic
    
    # Language: Strong, steady growth (starts high, grows consistently)
    language_base = 75 + (progress_factor * 15)  # 75-90 range
    language_score = int(language_base + random.uniform(-4, 6))
    
    # Cognitive: Moderate growth with more variation (starts medium, grows steadily)
    cognitive_base = 65 + (progress_factor * 20)  # 65-85 range
    cognitive_score = int(cognitive_base + random.uniform(-5, 5))
    
    # Emotional: Slower, more variable growth (starts lower, grows gradually)
    emotional_base = 70 + (progress_factor * 12)  # 70-82 range
    emotional_score = int(emotional_base + random.uniform(-6, 4))
    
    # Social: Moderate growth, some plateaus (starts medium-low, grows with dips)
    social_base = 68 + (progress_factor * 18)  # 68-86 range
    # Add occasional dips to make it more realistic
    if random.random() < 0.15:  # 15% chance of a dip
        social_score = int(social_base - 8 + random.uniform(-3, 3))
    else:
        social_score = int(social_base + random.uniform(-4, 6))
    
    # Creativity: High variability, strong growth (starts medium, can spike)
    creativity_base = 72 + (progress_factor * 16)  # 72-88 range
    # Occasional creative bursts
    if random.random() < 0.2:  # 20% chance of a creative burst
        creativity_score = int(creativity_base + 10 + random.uniform(-2, 5))
    else:
        creativity_score = int(creativity_base + random.uniform(-5, 5))
    
    # Physical: Steady, moderate growth (starts medium, grows consistently)
    physical_base = 70 + (progress_factor * 15)  # 70-85 range
    physical_score = int(physical_base + random.uniform(-4, 4))
    
    # Daily insight examples (more varied)
    insights = [
        f"{CHILD_NAME} used {8 + session_num + random.randint(0, 5)} new words today, including 'magnificent' and 'investigate'! His vocabulary is growing faster than 75% of kids his age.",
        f"{CHILD_NAME} asked {10 + session_num + random.randint(0, 3)} thoughtful questions today, showing strong curiosity and critical thinking skills.",
        f"{CHILD_NAME} demonstrated excellent storytelling abilities, creating narratives with clear beginnings, middles, and ends.",
        f"{CHILD_NAME} showed empathy by recognizing emotions in others and expressing concern for their feelings.",
        f"{CHILD_NAME} used complex sentences with conjunctions like 'because' and 'so', showing advanced language development.",
        f"{CHILD_NAME} initiated {2 + random.randint(0, 2)} conversation topics today, showing growing confidence in communication.",
        f"{CHILD_NAME} used {5 + random.randint(0, 3)} emotion words today, demonstrating developing emotional vocabulary.",
    ]
    
    daily_insight = random.choice(insights)
    
    # Language details
    vocabulary_size = 800 + int(session_num * 3.5) + random.randint(-10, 15)
    sentence_complexity = 6.5 + (session_num * 0.08) + random.uniform(-0.2, 0.2)
    grammar_accuracy = 75 + int(progress_factor * 15) + random.randint(-5, 5)
    question_frequency = 10 + session_num + random.randint(0, 4)
    
    # Engagement metrics
    session_duration = 180 + random.randint(-30, 60)  # 2.5-4 minutes
    conversation_turns = 40 + session_num + random.randint(-5, 10)
    child_initiated_topics = 2 + random.randint(0, 3)
    
    # AI metadata
    top_strength = random.choice(STRENGTHS_POOL)
    growth_area = random.choice(GROWTH_AREAS_POOL)
    suggested_activity = random.choice(ACTIVITIES_POOL).replace("{CHILD_NAME}", CHILD_NAME)
    
    # Emotional intelligence
    emotion_words_used = 5 + random.randint(0, 4)
    empathy_indicators = 2 + random.randint(0, 2)
    
    # Cognitive patterns
    reasoning_language_count = 3 + random.randint(0, 2)  # "because", "so", "if"
    abstract_thinking_score = 70 + int(progress_factor * 20) + random.randint(-5, 5)
    curiosity_score = 80 + int(session_num * 0.3) + random.randint(-5, 5)
    
    # Speech patterns
    speech_clarity_score = 88 + random.randint(-3, 5)
    sounds_to_practice = random.choice([
        [],
        ["r"],
        ["th"],
        ["r", "s"],
        []
    ])
    
    # Development snapshot
    development_snapshot = {
        "language": {
            "level": "strong" if language_score > 80 else "growing",
            "score": language_score
        },
        "cognitive": {
            "level": "strong" if cognitive_score > 75 else "growing",
            "score": cognitive_score
        },
        "emotional": {
            "level": "growing" if emotional_score > 70 else "emerging",
            "score": emotional_score
        },
        "social": {
            "level": "growing" if social_score > 75 else "emerging",
            "score": social_score
        },
        "creativity": {
            "level": "strong" if creativity_score > 85 else "growing",
            "score": creativity_score
        },
        "physical": {
            "level": "on_track",
            "score": physical_score
        }
    }
    
    # Strengths (pick 2-3)
    strengths = [
        {
            "title": top_strength,
            "evidence": f"{CHILD_NAME} demonstrated this strength in today's conversation.",
            "why_matters": "This strength supports future learning and social development."
        }
    ]
    if random.random() > 0.5:
        strengths.append({
            "title": random.choice([s for s in STRENGTHS_POOL if s != top_strength]),
            "evidence": f"Additional evidence of {CHILD_NAME}'s development.",
            "why_matters": "Multiple strengths indicate well-rounded development."
        })
    
    # Growth opportunities
    growth_opportunities = [
        {
            "area": growth_area,
            "current": f"Currently developing {growth_area.lower()}",
            "next_step": f"Practice {growth_area.lower()} through play-based activities"
        }
    ]
    
    # Personalized activities
    activities = [
        {
            "title": suggested_activity,
            "duration": f"{10 + random.randint(0, 10)} minutes",
            "materials": ["Varies by activity"],
            "instructions": f"Engage with {CHILD_NAME} in this activity to support development.",
            "impact_areas": ["language", "cognitive"],
            "based_on_interests": ["current interests"]
        }
    ]
    
    # Milestone progress
    milestone_progress = {
        "on_track": [
            "Uses 4-5 word sentences",
            "Tells stories with details",
            "Counts to 10",
            "Sorts by color/size"
        ],
        "emerging": [
            "Asks 'why' questions",
            "Understands time concepts"
        ],
        "ahead": [
            "Uses complex sentences",
            "Shows empathy"
        ]
    }
    
    # Vocabulary analysis
    vocabulary_analysis = {
        "vocabulary_size_estimate": vocabulary_size,
        "sentence_complexity": round(sentence_complexity, 1),
        "question_frequency": question_frequency,
        "story_coherence": "high",
        "conversation_turns": conversation_turns
    }
    
    # Cognitive indicators
    cognitive_indicators = {
        "reasoning_language": ["because", "so", "if-then"],
        "abstract_concepts": ["pretend", "imagine", "maybe"],
        "problem_solving_attempts": 8 + session_num,
        "curiosity_score": curiosity_score
    }
    
    # Emotional intelligence
    emotional_intelligence = {
        "emotion_words_used": ["happy", "sad", "frustrated", "excited", "proud"][:emotion_words_used],
        "empathy_indicators": ["she feels", "he wants", "they might be"][:empathy_indicators],
        "self_awareness": ["I think", "I feel", "I want"],
        "emotional_regulation": "developing"
    }
    
    # Social skills
    social_skills = {
        "turn_taking": "appropriate",
        "politeness_markers": ["please", "thank you", "excuse me"],
        "perspective_taking": "emerging",
        "sharing_language": ["we can", "let's", "together"]
    }
    
    # Creativity
    creativity_imagination = {
        "pretend_play_language": ["let's pretend", "imagine if"],
        "novel_word_combinations": 15 + session_num,
        "storytelling_originality": "high",
        "humor_attempts": 3 + (session_num % 2)
    }
    
    # Full analysis structure
    analysis = {
        "daily_insight": daily_insight,
        "development_snapshot": development_snapshot,
        "strengths": strengths,
        "growth_opportunities": growth_opportunities,
        "personalized_activities": activities,
        "milestone_progress": milestone_progress,
        "vocabulary_analysis": vocabulary_analysis,
        "cognitive_indicators": cognitive_indicators,
        "emotional_intelligence": emotional_intelligence,
        "social_skills": social_skills,
        "creativity_imagination": creativity_imagination,
        "parent_encouragement": f"Keep up the great conversations! {CHILD_NAME} is making wonderful progress."
    }
    
    # Return both analysis and enriched fields
    return {
        "analysis": analysis,
        "language_score": language_score,
        "cognitive_score": cognitive_score,
        "emotional_score": emotional_score,
        "social_score": social_score,
        "creativity_score": creativity_score,
        "vocabulary_size": vocabulary_size,
        "sentence_complexity": round(sentence_complexity, 1),
        "grammar_accuracy": grammar_accuracy,
        "question_frequency": question_frequency,
        "session_duration": session_duration,
        "conversation_turns": conversation_turns,
        "child_initiated_topics": child_initiated_topics,
        "daily_insight": daily_insight,
        "top_strength": top_strength,
        "growth_area": growth_area,
        "suggested_activity": suggested_activity,
        "emotion_words_used": emotion_words_used,
        "empathy_indicators": empathy_indicators,
        "reasoning_language_count": reasoning_language_count,
        "abstract_thinking_score": abstract_thinking_score,
        "curiosity_score": curiosity_score,
        "speech_clarity_score": speech_clarity_score,
        "sounds_to_practice": sounds_to_practice
    }

def create_dummy_profile():
    """Create a complete dummy child profile with 3 months of enriched data"""
    
    print("="*70)
    print("🎨 Creating Enriched Dummy Child Profile in Snowflake")
    print("="*70)
    print()
    
    # Initialize Snowflake service
    snowflake = SnowflakeService()
    
    if not snowflake.is_available():
        print("❌ Snowflake service not available")
        print("   Please check your SNOWFLAKE_* environment variables")
        return False
    
    print("✅ Snowflake connection established")
    print()
    
    try:
        cursor = snowflake.conn.cursor()
        
        # 1. Create user profile
        print(f"📝 Creating user profile for {CHILD_NAME} (ID: {DUMMY_CHILD_ID})...")
        
        profile_data = {
            "name": CHILD_NAME,
            "age": CHILD_AGE,
            "location": {
                "city": "New York",
                "state": "NY",
                "country": "USA"
            },
            "learning_goals": ["reading", "math", "social skills"],
            "preferences": {
                "interests": ["dinosaurs", "space", "building", "storytelling"],
                "activity_types": ["hands-on", "creative", "social"]
            }
        }
        
        # Check if user exists
        cursor.execute("SELECT user_id FROM user_profiles WHERE user_id = %s", (DUMMY_CHILD_ID,))
        exists = cursor.fetchone()
        
        if exists:
            print("   ⚠️  User already exists, updating...")
            preferences = profile_data.get('preferences', {})
            if profile_data.get('location'):
                preferences['location'] = profile_data.get('location')
            
            cursor.execute("""
                UPDATE user_profiles
                SET name = %s, age = %s, updated_at = %s,
                    learning_goals = TO_VARIANT(PARSE_JSON(%s)), 
                    preferences_json = TO_VARIANT(PARSE_JSON(%s)), 
                    location_json = TO_VARIANT(PARSE_JSON(%s))
                WHERE user_id = %s
            """, (
                profile_data.get('name'),
                profile_data.get('age'),
                datetime.now(timezone.utc),
                json.dumps(profile_data.get('learning_goals', [])),
                json.dumps(preferences),
                json.dumps(profile_data.get('location', {})),
                DUMMY_CHILD_ID
            ))
        else:
            print("   ✅ Creating new user profile...")
            preferences = profile_data.get('preferences', {})
            if profile_data.get('location'):
                preferences['location'] = profile_data.get('location')
            
            cursor.execute("""
                INSERT INTO user_profiles (
                    user_id, name, age, created_at, updated_at,
                    learning_goals, preferences_json, location_json
                )
                SELECT 
                    %s, %s, %s, %s, %s,
                    PARSE_JSON(%s), PARSE_JSON(%s), PARSE_JSON(%s)
            """, (
                DUMMY_CHILD_ID,
                profile_data.get('name'),
                profile_data.get('age'),
                datetime.now(timezone.utc),
                datetime.now(timezone.utc),
                json.dumps(profile_data.get('learning_goals', [])),
                json.dumps(preferences),
                json.dumps(profile_data.get('location', {}))
            ))
        
        print("   ✅ User profile created/updated")
        print()
        
        # 2. Create development sessions (3 months = 90 days, ~45 sessions)
        print("📊 Creating development sessions (3 months of data)...")
        
        # Clear existing sessions for this child
        cursor.execute("DELETE FROM child_development_sessions WHERE child_id = %s", (DUMMY_CHILD_ID,))
        print("   🗑️  Cleared existing sessions")
        
        num_sessions = 45  # ~3 sessions per week over 3 months
        base_date = datetime.now(timezone.utc) - timedelta(days=90)
        
        # Generate sessions spread over 90 days
        session_dates = sorted([base_date + timedelta(days=random.randint(0, 89)) for _ in range(num_sessions)])
        
        for i, session_date in enumerate(session_dates):
            session_id = str(uuid.uuid4())
            days_ago = (datetime.now(timezone.utc) - session_date).days
            
            enriched_data = create_enriched_analysis(i, num_sessions, days_ago)
            analysis = enriched_data["analysis"]
            
            # Extract development scores
            dev_snapshot = analysis.get('development_snapshot', {})
            development_scores = {
                "language": dev_snapshot.get('language', {}).get('score', 0),
                "cognitive": dev_snapshot.get('cognitive', {}).get('score', 0),
                "emotional": dev_snapshot.get('emotional', {}).get('score', 0),
                "social": dev_snapshot.get('social', {}).get('score', 0),
                "creativity": dev_snapshot.get('creativity', {}).get('score', 0),
                "physical": dev_snapshot.get('physical', {}).get('score', 0)
            }
            
            # Get conversation template
            topic, conversation = random.choice(CONVERSATION_TEMPLATES)
            transcript = "\n".join(conversation)
            transcript_length = len(transcript)
            
            # Insert session with ALL enriched fields
            cursor.execute("""
                INSERT INTO child_development_sessions (
                    session_id, child_id, child_name, child_age, timestamp,
                    transcript, transcript_length, audio_path, session_context, analysis,
                    development_scores, vocabulary_analysis, cognitive_indicators,
                    emotional_intelligence, social_skills, creativity_imagination,
                    speech_clarity, 
                    -- Enriched fields
                    language_score, cognitive_score, emotional_score, social_score, creativity_score,
                    vocabulary_size, sentence_complexity, grammar_accuracy, question_frequency,
                    session_duration, conversation_turns, child_initiated_topics,
                    daily_insight, top_strength, growth_area, suggested_activity,
                    emotion_words_used, empathy_indicators,
                    reasoning_language_count, abstract_thinking_score, curiosity_score,
                    speech_clarity_score, sounds_to_practice,
                    created_at
                )
                SELECT 
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, PARSE_JSON(%s), PARSE_JSON(%s),
                    PARSE_JSON(%s), PARSE_JSON(%s), PARSE_JSON(%s),
                    PARSE_JSON(%s), PARSE_JSON(%s), PARSE_JSON(%s),
                    PARSE_JSON(%s),
                    -- Enriched fields
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s,
                    %s, %s, %s,
                    %s, PARSE_JSON(%s),
                    %s
            """, (
                session_id,
                DUMMY_CHILD_ID,
                CHILD_NAME,
                CHILD_AGE,
                session_date,
                transcript.strip(),
                transcript_length,
                f"audio/session_{session_id}.mp3",
                json.dumps({"duration_minutes": enriched_data["session_duration"] // 60, "context": "evening_conversation", "topic": topic}),
                json.dumps(analysis),
                json.dumps(development_scores),
                json.dumps(analysis.get('vocabulary_analysis', {})),
                json.dumps(analysis.get('cognitive_indicators', {})),
                json.dumps(analysis.get('emotional_intelligence', {})),
                json.dumps(analysis.get('social_skills', {})),
                json.dumps(analysis.get('creativity_imagination', {})),
                json.dumps({"intelligibility": enriched_data["speech_clarity_score"], "age_appropriate": True}),
                # Enriched fields
                enriched_data["language_score"],
                enriched_data["cognitive_score"],
                enriched_data["emotional_score"],
                enriched_data["social_score"],
                enriched_data["creativity_score"],
                enriched_data["vocabulary_size"],
                enriched_data["sentence_complexity"],
                enriched_data["grammar_accuracy"],
                enriched_data["question_frequency"],
                enriched_data["session_duration"],
                enriched_data["conversation_turns"],
                enriched_data["child_initiated_topics"],
                enriched_data["daily_insight"],
                enriched_data["top_strength"],
                enriched_data["growth_area"],
                enriched_data["suggested_activity"],
                enriched_data["emotion_words_used"],
                enriched_data["empathy_indicators"],
                enriched_data["reasoning_language_count"],
                enriched_data["abstract_thinking_score"],
                enriched_data["curiosity_score"],
                enriched_data["speech_clarity_score"],
                json.dumps(enriched_data["sounds_to_practice"]),
                session_date
            ))
            
            if (i + 1) % 10 == 0:
                print(f"   ✅ Created {i + 1}/{num_sessions} sessions...")
        
        print(f"   ✅ Created {num_sessions} development sessions")
        print()
        
        # 3. Create trend data (daily aggregates for 90 days)
        print("📈 Creating trend data (90 days)...")
        
        # Clear existing trends
        cursor.execute("DELETE FROM child_development_trends WHERE child_id = %s", (DUMMY_CHILD_ID,))
        print("   🗑️  Cleared existing trends")
        
        for day in range(90):
            trend_id = str(uuid.uuid4())
            trend_date = base_date + timedelta(days=day)
            
            # Calculate progressive scores with DIFFERENT patterns for each score type
            progress = day / 90.0
            
            # Language: Strong, steady growth (starts high, grows consistently)
            # Range: 70-95, with steady upward trend
            language_score = 70 + (progress * 20) + random.uniform(-3, 4)
            # Add occasional spikes for language milestones
            if random.random() < 0.1:  # 10% chance of language breakthrough
                language_score += random.uniform(5, 10)
            
            # Cognitive: Moderate growth with more variation (starts medium, grows steadily)
            # Range: 60-90, with more variability
            cognitive_score = 60 + (progress * 25) + random.uniform(-5, 6)
            # Cognitive can have plateaus
            if random.random() < 0.15:  # 15% chance of plateau
                cognitive_score -= random.uniform(3, 7)
            
            # Emotional: Slower, more variable growth (starts lower, grows gradually)
            # Range: 65-85, slower growth rate
            emotional_score = 65 + (progress * 15) + random.uniform(-6, 5)
            # Emotional development can be more volatile
            if random.random() < 0.2:  # 20% chance of emotional variation
                emotional_score += random.uniform(-8, 8)
            
            # Social: Moderate growth, some plateaus (starts medium-low, grows with dips)
            # Range: 55-85, with occasional dips
            social_score = 55 + (progress * 25) + random.uniform(-4, 5)
            # Social skills can dip occasionally
            if random.random() < 0.12:  # 12% chance of social dip
                social_score -= random.uniform(5, 10)
            # But also can have social breakthroughs
            if random.random() < 0.08:  # 8% chance of social breakthrough
                social_score += random.uniform(8, 12)
            
            # Creativity: High variability, strong growth (starts medium, can spike)
            # Range: 70-95, most variable
            creativity_score = 70 + (progress * 20) + random.uniform(-8, 10)
            # Creative bursts are common
            if random.random() < 0.25:  # 25% chance of creative burst
                creativity_score += random.uniform(10, 15)
            # But also creative lulls
            if random.random() < 0.1:  # 10% chance of creative lull
                creativity_score -= random.uniform(5, 10)
            
            # Ensure scores stay in reasonable bounds (0-100)
            language_score = max(0, min(100, round(language_score, 1)))
            cognitive_score = max(0, min(100, round(cognitive_score, 1)))
            emotional_score = max(0, min(100, round(emotional_score, 1)))
            social_score = max(0, min(100, round(social_score, 1)))
            creativity_score = max(0, min(100, round(creativity_score, 1)))
            
            # Get vocabulary and complexity from sessions
            vocab_size = 800 + int(day * 2.2) + random.randint(-5, 10)
            complexity = 6.5 + (day * 0.04) + random.uniform(-0.1, 0.1)
            
            # Strengths detected
            strengths = random.sample(STRENGTHS_POOL, k=random.randint(2, 4))
            
            growth_areas = random.sample(GROWTH_AREAS_POOL, k=random.randint(1, 3))
            
            milestones = {
                "on_track": ["Uses 4-5 word sentences", "Tells stories with details"],
                "emerging": ["Asks 'why' questions"],
                "ahead": ["Uses complex sentences"]
            }
            
            cursor.execute("""
                INSERT INTO child_development_trends (
                    trend_id, child_id, date,
                    language_score, cognitive_score, emotional_score,
                    social_score, creativity_score,
                    vocabulary_size, sentence_complexity,
                    question_frequency, curiosity_score,
                    strengths_detected, growth_areas, milestones_progress,
                    created_at
                )
                SELECT 
                    %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    PARSE_JSON(%s), PARSE_JSON(%s), PARSE_JSON(%s),
                    %s
            """, (
                trend_id,
                DUMMY_CHILD_ID,
                trend_date.date(),
                language_score,
                cognitive_score,
                emotional_score,
                social_score,
                creativity_score,
                vocab_size,
                round(complexity, 1),
                10 + int(day * 0.2) + random.randint(0, 3),
                80 + (day * 0.3) + random.uniform(-2, 2),
                json.dumps(strengths),
                json.dumps(growth_areas),
                json.dumps(milestones),
                trend_date
            ))
            
            if (day + 1) % 30 == 0:
                print(f"   ✅ Created {day + 1}/90 days of trend data...")
        
        print("   ✅ Created 90 days of trend data")
        print()
        
        # Commit all changes
        snowflake.conn.commit()
        cursor.close()
        
        print("="*70)
        print("✅ Enriched Dummy Profile Created Successfully!")
        print("="*70)
        print()
        print(f"📋 Child ID: {DUMMY_CHILD_ID}")
        print(f"👤 Name: {CHILD_NAME}")
        print(f"🎂 Age: {CHILD_AGE}")
        print(f"📊 Sessions: {num_sessions} (over 3 months)")
        print(f"📈 Trends: 90 days")
        print()
        print("✨ Enriched Data Includes:")
        print("   - Core development scores (language, cognitive, emotional, social, creativity)")
        print("   - Language details (vocabulary, sentence complexity, grammar)")
        print("   - Engagement metrics (duration, turns, child-initiated topics)")
        print("   - AI metadata (daily insights, strengths, growth areas)")
        print("   - Emotional intelligence metrics")
        print("   - Cognitive patterns (reasoning, abstract thinking, curiosity)")
        print("   - Speech clarity scores")
        print()
        print("🌐 View in Dashboard:")
        print(f"   1. Open http://localhost:5173")
        print(f"   2. Enter child ID: {DUMMY_CHILD_ID}")
        print(f"   3. Click 'Refresh'")
        print()
        print("📊 View in Snowflake:")
        print("   - Use queries from snowflake_dashboard_queries.sql")
        print("   - All enriched columns are now available for analysis")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating dummy profile: {e}")
        import traceback
        traceback.print_exc()
        snowflake.conn.rollback()
        return False

if __name__ == "__main__":
    success = create_dummy_profile()
    sys.exit(0 if success else 1)
