#!/usr/bin/env python3
"""
Create dummy user and child profiles for testing
"""

import os
import sys
import json
import uuid
import random
from datetime import datetime, timezone
from dotenv import load_dotenv

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import services
from services.firebase_service import FirebaseService
from services.snowflake_service import SnowflakeService

# Load environment variables
load_dotenv()

# Sample data
CHILD_NAMES = ["Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason", "Isabella", "Lucas"]
LEARNING_GOALS = [
    ["reading", "math", "science"],
    ["language", "creativity", "social skills"],
    ["problem solving", "critical thinking"],
    ["vocabulary", "storytelling"],
    ["numbers", "shapes", "colors"]
]

PREFERENCES_TEMPLATES = [
    {
        "voice_id": "default",
        "learning_style": "visual",
        "difficulty_level": "beginner",
        "interests": ["animals", "nature", "outdoor activities"]
    },
    {
        "voice_id": "default",
        "learning_style": "kinesthetic",
        "difficulty_level": "intermediate",
        "interests": ["building", "construction", "robots"]
    },
    {
        "voice_id": "default",
        "learning_style": "auditory",
        "difficulty_level": "beginner",
        "interests": ["music", "songs", "rhymes"]
    }
]

LOCATIONS = [
    {"city": "New York", "state": "NY", "country": "USA", "zipcode": "10001"},
    {"city": "Los Angeles", "state": "CA", "country": "USA", "zipcode": "90001"},
    {"city": "Chicago", "state": "IL", "country": "USA", "zipcode": "60601"},
    {"city": "Houston", "state": "TX", "country": "USA", "zipcode": "77001"},
    {"city": "Phoenix", "state": "AZ", "country": "USA", "zipcode": "85001"}
]


def create_user_profile(user_id: str = None, name: str = None, age: int = None):
    """Create a dummy user profile"""
    if not user_id:
        user_id = f"user_{uuid.uuid4().hex[:8]}"
    
    if not name:
        name = random.choice(CHILD_NAMES)
    
    if not age:
        age = random.randint(3, 8)
    
    profile_data = {
        'name': name,
        'age': age,
        'learning_goals': random.choice(LEARNING_GOALS),
        'preferences': random.choice(PREFERENCES_TEMPLATES).copy(),
        'location': random.choice(LOCATIONS).copy()
    }
    
    return user_id, profile_data


def create_child_profile(child_id: str = None, child_name: str = None, child_age: int = None):
    """Create a dummy child profile"""
    if not child_id:
        child_id = f"child_{uuid.uuid4().hex[:8]}"
    
    if not child_name:
        child_name = random.choice(CHILD_NAMES)
    
    if not child_age:
        child_age = random.randint(3, 8)
    
    profile_data = {
        'child_id': child_id,
        'child_name': child_name,
        'child_age': child_age,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'interests': random.choice(PREFERENCES_TEMPLATES)['interests'],
        'learning_style': random.choice(PREFERENCES_TEMPLATES)['learning_style']
    }
    
    return child_id, profile_data


def main():
    """Main function to create dummy profiles"""
    print("Creating dummy profiles...")
    
    # Initialize services
    firebase_service = FirebaseService()
    snowflake_service = SnowflakeService()
    
    # Check service availability
    firebase_available = firebase_service.is_available()
    snowflake_available = snowflake_service.is_available()
    
    if not firebase_available and not snowflake_available:
        print("ERROR: Neither Firebase nor Snowflake is available!")
        print("Please check your environment variables and credentials.")
        return
    
    print(f"Firebase: {'✓ Available' if firebase_available else '✗ Not available'}")
    print(f"Snowflake: {'✓ Available' if snowflake_available else '✗ Not available'}")
    print()
    
    # Create user profiles
    num_users = int(input("How many user profiles to create? (default: 3): ") or "3")
    print(f"\nCreating {num_users} user profile(s)...")
    
    created_users = []
    for i in range(num_users):
        user_id, profile_data = create_user_profile()
        
        # Save to Firebase
        if firebase_available:
            try:
                firebase_service.update_user_profile(user_id, profile_data)
                print(f"  ✓ Created user profile in Firebase: {user_id} ({profile_data['name']}, age {profile_data['age']})")
            except Exception as e:
                print(f"  ✗ Failed to create user in Firebase: {e}")
        
        # Save to Snowflake
        if snowflake_available:
            try:
                snowflake_service.update_user_profile(user_id, profile_data)
                print(f"  ✓ Created user profile in Snowflake: {user_id}")
            except Exception as e:
                print(f"  ✗ Failed to create user in Snowflake: {e}")
        
        created_users.append({
            'user_id': user_id,
            'profile': profile_data
        })
    
    # Create child profiles (if Firebase is available)
    if firebase_available:
        create_children = input("\nCreate child profiles? (y/n, default: y): ").lower() or "y"
        if create_children == 'y':
            num_children = int(input("How many child profiles to create? (default: 2): ") or "2")
            print(f"\nCreating {num_children} child profile(s)...")
            
            for i in range(num_children):
                child_id, profile_data = create_child_profile()
                
                try:
                    # Save to Firebase child_profiles collection
                    if firebase_service.db:
                        firebase_service.db.collection('child_profiles').document(child_id).set(profile_data)
                        print(f"  ✓ Created child profile: {child_id} ({profile_data['child_name']}, age {profile_data['child_age']})")
                except Exception as e:
                    print(f"  ✗ Failed to create child profile: {e}")
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Created {len(created_users)} user profile(s):")
    for user in created_users:
        print(f"  - {user['user_id']}: {user['profile']['name']} (age {user['profile']['age']})")
        print(f"    Learning goals: {', '.join(user['profile']['learning_goals'])}")
        print(f"    Location: {user['profile']['location']['city']}, {user['profile']['location']['state']}")
    
    print("\nTo use these profiles, set the X-User-ID header to one of the user_ids above.")
    print("Example API call:")
    if created_users:
        example_id = created_users[0]['user_id']
        print(f"  curl -H 'X-User-ID: {example_id}' http://localhost:5000/api/user/profile")


if __name__ == "__main__":
    main()

