"""
Claude 3 Sonnet Service - Structured Learning Plans & Quizzes
"""

import os
import logging
import json
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class ClaudeService:
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.client = None
        if self.api_key:
            try:
                self.client = Anthropic(api_key=self.api_key)
                logger.info("Claude service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Claude: {e}")
    
    def is_available(self):
        """Check if Claude service is available"""
        return self.client is not None
    
    def generate_lesson_plan(self, topic, user_profile, parameters):
        """Generate structured lesson plan using Claude 3 Sonnet"""
        if not self.client:
            raise Exception("Claude service not available")
        
        try:
            # Build lesson plan prompt
            prompt = self._build_lesson_prompt(topic, user_profile, parameters)
            
            # Call Claude API
            message = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4096,
                temperature=0.7,
                system="You are an expert educational curriculum designer. Create comprehensive, engaging lesson plans tailored to individual students.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response_text = message.content[0].text
            
            # Parse structured response
            lesson_plan = self._parse_lesson_plan(response_text)
            
            logger.info(f"Generated lesson plan for: {topic}")
            return lesson_plan
            
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise
    
    def generate_quiz(self, topic, user_profile, parameters):
        """Generate interactive quiz using Claude 3 Sonnet"""
        if not self.client:
            raise Exception("Claude service not available")
        
        try:
            # Build quiz prompt
            prompt = self._build_quiz_prompt(topic, user_profile, parameters)
            
            # Call Claude API
            message = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=3072,
                temperature=0.6,
                system="You are an expert at creating engaging, educational quizzes. Generate well-structured questions with clear explanations.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response_text = message.content[0].text
            
            # Parse quiz structure
            quiz = self._parse_quiz(response_text)
            
            logger.info(f"Generated quiz for: {topic}")
            return quiz
            
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise
    
    def generate_curriculum(self, topic, user_profile, parameters):
        """Generate multi-week curriculum using Claude 3 Sonnet"""
        if not self.client:
            raise Exception("Claude service not available")
        
        try:
            # Build curriculum prompt
            prompt = self._build_curriculum_prompt(topic, user_profile, parameters)
            
            # Call Claude API
            message = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4096,
                temperature=0.7,
                system="You are a master curriculum designer. Create comprehensive, progressive learning paths.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response_text = message.content[0].text
            
            # Parse curriculum structure
            curriculum = self._parse_curriculum(response_text)
            
            logger.info(f"Generated curriculum for: {topic}")
            return curriculum
            
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise
    
    def _build_lesson_prompt(self, topic, user_profile, parameters):
        """Build prompt for lesson plan generation"""
        duration = parameters.get('duration', '30 minutes')
        difficulty = parameters.get('difficulty', user_profile.get('preferences', {}).get('difficulty_level', 'beginner') if user_profile else 'beginner')
        
        prompt = f"""Create a detailed lesson plan for the topic: "{topic}"

Target audience: """
        
        if user_profile:
            name = user_profile.get('name')
            age = user_profile.get('age')
            prompt += f"{name}, {age} years old" if age else name
            prompt += f"\nDifficulty level: {difficulty}"
            
            learning_progress = user_profile.get('learning_progress', {})
            if learning_progress:
                prompt += f"\nPrevious experience: {', '.join([k for k, v in learning_progress.items() if v > 0.7])}"
        else:
            prompt += f"{difficulty} level learner"
        
        prompt += f"""

Duration: {duration}

Please provide a structured lesson plan with:
1. Learning Objectives (3-5 clear, measurable goals)
2. Introduction (engaging hook)
3. Core Content (broken into digestible sections)
4. Activities (interactive elements for AR environment)
5. Visual Aids (suggestions for 3D models, diagrams, animations)
6. Assessment (check for understanding)
7. Key Takeaways
8. Resources for Further Learning

Format the response in clear sections. Be specific about AR interactions."""
        
        return prompt
    
    def _build_quiz_prompt(self, topic, user_profile, parameters):
        """Build prompt for quiz generation"""
        num_questions = parameters.get('num_questions', 5)
        question_types = parameters.get('types', ['multiple_choice', 'true_false', 'short_answer'])
        difficulty = parameters.get('difficulty', user_profile.get('preferences', {}).get('difficulty_level', 'beginner') if user_profile else 'beginner')
        
        prompt = f"""Create an engaging quiz on: "{topic}"

Number of questions: {num_questions}
Question types: {', '.join(question_types)}
Difficulty: {difficulty}

"""
        
        if user_profile:
            prompt += f"Student: {user_profile.get('name')}\n"
            learning_progress = user_profile.get('learning_progress', {})
            if topic in learning_progress:
                prompt += f"Current mastery level: {learning_progress[topic]*100:.0f}%\n"
        
        prompt += """
For each question, provide:
1. Question text
2. Options (for multiple choice)
3. Correct answer
4. Detailed explanation
5. Visual suggestion (for AR display)
6. Difficulty level

Format as a structured list. Make questions engaging and educational."""
        
        return prompt
    
    def _build_curriculum_prompt(self, topic, user_profile, parameters):
        """Build prompt for curriculum generation"""
        duration_weeks = parameters.get('duration_weeks', 4)
        
        prompt = f"""Design a comprehensive {duration_weeks}-week curriculum for: "{topic}"

"""
        
        if user_profile:
            name = user_profile.get('name')
            age = user_profile.get('age')
            prompt += f"Student: {name}, {age} years old\n"
            prompt += f"Learning goals: {', '.join(user_profile.get('learning_goals', ['general mastery']))}\n"
        
        prompt += f"""
Create a progressive learning path with:
1. Weekly breakdown with themes
2. Daily objectives and activities
3. Milestone assessments
4. AR experiences for each week
5. Projects and practical applications
6. Success metrics

Make it engaging, achievable, and adaptive."""
        
        return prompt
    
    def _parse_lesson_plan(self, response_text):
        """Parse lesson plan from Claude response"""
        # Simple parsing - could be enhanced with more sophisticated extraction
        return {
            'type': 'lesson_plan',
            'content': response_text,
            'sections': self._extract_sections(response_text),
            'duration': '30 minutes',
            'format': 'structured'
        }
    
    def _parse_quiz(self, response_text):
        """Parse quiz from Claude response"""
        # Extract questions (basic parsing)
        questions = []
        lines = response_text.split('\n')
        
        current_question = None
        for line in lines:
            line = line.strip()
            if line.startswith('Question ') or line.startswith('Q'):
                if current_question:
                    questions.append(current_question)
                current_question = {'question': line, 'options': [], 'explanation': ''}
            elif current_question and line.startswith(('A)', 'B)', 'C)', 'D)', 'a)', 'b)', 'c)', 'd)')):
                current_question['options'].append(line)
        
        if current_question:
            questions.append(current_question)
        
        return {
            'type': 'quiz',
            'questions': questions,
            'total_questions': len(questions),
            'full_content': response_text
        }
    
    def _parse_curriculum(self, response_text):
        """Parse curriculum from Claude response"""
        return {
            'type': 'curriculum',
            'overview': response_text[:500],
            'full_content': response_text,
            'weeks': self._extract_weeks(response_text)
        }
    
    def _extract_sections(self, text):
        """Extract sections from formatted text"""
        sections = []
        current_section = None
        
        for line in text.split('\n'):
            line = line.strip()
            if line and (line.startswith('#') or line.endswith(':')):
                if current_section:
                    sections.append(current_section)
                current_section = {'title': line.strip('#: '), 'content': ''}
            elif current_section:
                current_section['content'] += line + '\n'
        
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def _extract_weeks(self, text):
        """Extract weekly breakdown from curriculum"""
        weeks = []
        lines = text.split('\n')
        
        for line in lines:
            if 'week' in line.lower() and ':' in line:
                weeks.append(line.strip())
        
        return weeks[:8]  # Max 8 weeks

