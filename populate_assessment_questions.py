#!/usr/bin/env python3
"""
Script to populate assessment questions for soft skills evaluation.
All questions are in English and follow real workplace scenarios.
"""
import asyncio
import sys
import os
from datetime import datetime, timezone

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.soft_skills_practice.infrastructure.persistence.models.assessment_models import (
    AssessmentQuestion, 
    AssessmentQuestionOption,
    InitialAssessment
)
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

async def create_assessment_questions():
    """Create assessment questions for all soft skills"""
    
    questions_data = [
        # ACTIVE LISTENING (Communication)
        {
            "skill_type": "active_listening",
            "skill_name": "Active Listening",
            "scenario_text": "During a team meeting, your colleague Sarah presents an idea that you believe has significant flaws. The meeting is running long, and your manager seems eager to move forward with Sarah's proposal. Other team members appear to have concerns but aren't speaking up.",
            "question_text": "What is the most effective way to address your concerns about Sarah's proposal?",
            "options": [
                {"option_id": "A", "option_text": "Wait until after the meeting to speak privately with your manager about the flaws", "is_correct": False},
                {"option_id": "B", "option_text": "Respectfully ask clarifying questions during the meeting to highlight potential issues", "is_correct": True},
                {"option_id": "C", "option_text": "Directly point out the flaws in Sarah's proposal during the meeting", "is_correct": False},
                {"option_id": "D", "option_text": "Stay silent to avoid conflict and address it later if problems arise", "is_correct": False}
            ],
            "correct_answer_id": "B",
            "difficulty_level": 3,
            "explanation": "Asking clarifying questions demonstrates active listening while allowing you to address concerns constructively and giving everyone a chance to think through the issues together."
        },
        {
            "skill_type": "active_listening",
            "skill_name": "Active Listening",
            "scenario_text": "You need to deliver negative feedback to a team member who has been consistently missing deadlines. This person is generally hardworking but seems overwhelmed lately. You want to address the issue without damaging their motivation or your working relationship.",
            "question_text": "How should you approach this feedback conversation?",
            "options": [
                {"option_id": "A", "option_text": "Focus on the missed deadlines and explain the impact on the team's goals", "is_correct": False},
                {"option_id": "B", "option_text": "First listen to understand their perspective and challenges before addressing the issue", "is_correct": True},
                {"option_id": "C", "option_text": "Start by highlighting their positive qualities before addressing the deadline issues", "is_correct": False},
                {"option_id": "D", "option_text": "Ask them to explain why they keep missing deadlines", "is_correct": False}
            ],
            "correct_answer_id": "B",
            "difficulty_level": 2,
            "explanation": "Active listening involves understanding their perspective first, which provides crucial context for addressing the performance issues effectively."
        },
        
        # PUBLIC SPEAKING (Communication)
        {
            "skill_type": "public_speaking",
            "skill_name": "Public Speaking",
            "scenario_text": "You've been asked to present your team's quarterly results to senior management. The presentation is in two days, and you know some of the results are below expectations. You're feeling nervous about potential difficult questions.",
            "question_text": "What is the best approach to prepare for this high-stakes presentation?",
            "options": [
                {"option_id": "A", "option_text": "Focus on the positive results and minimize discussion of underperformance", "is_correct": False},
                {"option_id": "B", "option_text": "Prepare clear explanations for underperformance and actionable improvement plans", "is_correct": True},
                {"option_id": "C", "option_text": "Ask your manager to present the difficult parts while you handle the positive sections", "is_correct": False},
                {"option_id": "D", "option_text": "Practice your delivery but avoid preparing for potential difficult questions", "is_correct": False}
            ],
            "correct_answer_id": "B",
            "difficulty_level": 3,
            "explanation": "Effective public speaking requires transparency and preparation for difficult topics, showing accountability and forward-thinking leadership."
        },
        
        # TEAM MOTIVATION (Leadership)
        {
            "skill_type": "team_motivation",
            "skill_name": "Team Motivation",
            "scenario_text": "Your team is facing a tight deadline on a critical project. Two of your best team members are in disagreement about the technical approach, and their conflict is slowing down progress. Both have valid points, but you need to make a decision quickly to keep the project on track.",
            "question_text": "As the team leader, what is your best course of action?",
            "options": [
                {"option_id": "A", "option_text": "Choose the approach from your most experienced team member", "is_correct": False},
                {"option_id": "B", "option_text": "Facilitate a quick decision-making session with both members, set a deadline for resolution", "is_correct": True},
                {"option_id": "C", "option_text": "Make the decision yourself based on your understanding of the requirements", "is_correct": False},
                {"option_id": "D", "option_text": "Ask the team to vote on which approach to take", "is_correct": False}
            ],
            "correct_answer_id": "B",
            "difficulty_level": 4,
            "explanation": "Facilitating a structured decision-making process leverages team expertise while maintaining leadership control and keeping the team motivated through participation."
        },
        
        # DECISION MAKING (Leadership)
        {
            "skill_type": "decision_making",
            "skill_name": "Decision Making",
            "scenario_text": "You must choose between two qualified candidates for a critical role on your team. Candidate A has superior technical skills and relevant experience but poor communication abilities. Candidate B has good technical skills, excellent communication, and fits well with team culture, but lacks some specific experience.",
            "question_text": "What factors should most influence your hiring decision?",
            "options": [
                {"option_id": "A", "option_text": "Choose Candidate A for the technical expertise needed for immediate project success", "is_correct": False},
                {"option_id": "B", "option_text": "Evaluate which candidate's strengths best align with long-term team needs and growth", "is_correct": True},
                {"option_id": "C", "option_text": "Select Candidate B to maintain positive team dynamics and communication", "is_correct": False},
                {"option_id": "D", "option_text": "Delay the decision until you can find a candidate who meets all requirements", "is_correct": False}
            ],
            "correct_answer_id": "B",
            "difficulty_level": 4,
            "explanation": "Good decision-making considers both immediate needs and long-term impact, evaluating which option provides the best overall value for the team's success."
        },
        
        # COLLABORATION (Teamwork)
        {
            "skill_type": "collaboration",
            "skill_name": "Collaboration",
            "scenario_text": "Your team is working on a complex project with multiple components. One team member, Alex, is struggling with their assigned tasks and has fallen behind. This is starting to impact other team members' work. Alex is usually reliable but seems stressed about something personal.",
            "question_text": "How do you best support both Alex and the team's success?",
            "options": [
                {"option_id": "A", "option_text": "Offer to help Alex with their tasks while encouraging them to share what support they need", "is_correct": True},
                {"option_id": "B", "option_text": "Reassign Alex's tasks to other team members to keep the project on track", "is_correct": False},
                {"option_id": "C", "option_text": "Ask Alex to work extra hours to catch up with their commitments", "is_correct": False},
                {"option_id": "D", "option_text": "Report Alex's performance issues to management for guidance", "is_correct": False}
            ],
            "correct_answer_id": "A",
            "difficulty_level": 2,
            "explanation": "Offering support while opening communication shows true collaboration, addressing both the immediate project needs and team member wellbeing."
        },
        
        # ADAPTABILITY (Teamwork)
        {
            "skill_type": "adaptability",
            "skill_name": "Adaptability",
            "scenario_text": "Your company has just announced a major reorganization that will change your role significantly. You'll be working with a new team, using different tools, and focusing on areas outside your current expertise. Some colleagues are expressing frustration and resistance to the changes.",
            "question_text": "How do you best demonstrate adaptability in this situation?",
            "options": [
                {"option_id": "A", "option_text": "Focus on learning the new requirements and identify specific skills you need to develop", "is_correct": True},
                {"option_id": "B", "option_text": "Express your concerns to management about the impact on your current projects", "is_correct": False},
                {"option_id": "C", "option_text": "Wait to see how the changes unfold before making any adjustments", "is_correct": False},
                {"option_id": "D", "option_text": "Network with colleagues to find a role that better matches your current skills", "is_correct": False}
            ],
            "correct_answer_id": "A",
            "difficulty_level": 3,
            "explanation": "Proactively focusing on learning and skill development shows adaptability and helps you succeed in the new environment rather than resisting change."
        },
        
        # CONFLICT RESOLUTION (Leadership)
        {
            "skill_type": "conflict_resolution",
            "skill_name": "Conflict Resolution",
            "scenario_text": "Two team members, Maria and John, are in constant disagreement about project priorities. Maria believes the team should focus on quality and thorough testing, while John pushes for faster delivery to meet aggressive deadlines. Their arguments are becoming disruptive to the entire team.",
            "question_text": "What is the most effective approach to resolve this conflict?",
            "options": [
                {"option_id": "A", "option_text": "Meet with Maria and John separately to understand their underlying concerns", "is_correct": True},
                {"option_id": "B", "option_text": "Set clear priorities yourself and require both to follow your decision", "is_correct": False},
                {"option_id": "C", "option_text": "Organize a team meeting to let everyone vote on the approach", "is_correct": False},
                {"option_id": "D", "option_text": "Assign Maria and John to different aspects of the project to minimize interaction", "is_correct": False}
            ],
            "correct_answer_id": "A",
            "difficulty_level": 3,
            "explanation": "Understanding underlying concerns helps identify the root causes of conflict and enables finding solutions that address both parties' core needs."
        },
        
        # EMPATHY (Emotional Intelligence)
        {
            "skill_type": "empathy",
            "skill_name": "Empathy",
            "scenario_text": "During a team review meeting, your colleague James receives harsh criticism from the manager about a project failure. James visibly becomes upset and defensive, raising his voice and blaming external factors. The room becomes tense, and other team members look uncomfortable.",
            "question_text": "How do you best demonstrate empathy in this situation?",
            "options": [
                {"option_id": "A", "option_text": "Stay quiet and address the situation with James privately after the meeting", "is_correct": False},
                {"option_id": "B", "option_text": "Acknowledge the criticism's validity while suggesting a short break to regroup", "is_correct": True},
                {"option_id": "C", "option_text": "Defend James and point out that the criticism was too harsh", "is_correct": False},
                {"option_id": "D", "option_text": "Redirect the conversation to focus on solutions rather than blame", "is_correct": False}
            ],
            "correct_answer_id": "B",
            "difficulty_level": 4,
            "explanation": "Acknowledging emotions while creating space for people to regulate themselves shows empathy and helps de-escalate tense situations."
        },
        
        # CRITICAL THINKING (Problem Solving)
        {
            "skill_type": "critical_thinking",
            "skill_name": "Critical Thinking",
            "scenario_text": "Your company is considering adopting a new software platform that promises to increase productivity by 40%. The sales presentation was impressive, testimonials are positive, and the price is competitive. However, you're responsible for making the recommendation to senior management.",
            "question_text": "What critical thinking approach should you take before making your recommendation?",
            "options": [
                {"option_id": "A", "option_text": "Research independent reviews and analyze the methodology behind the productivity claims", "is_correct": True},
                {"option_id": "B", "option_text": "Request a trial period to test the software with a small group of users", "is_correct": False},
                {"option_id": "C", "option_text": "Compare the features and pricing with three competing solutions", "is_correct": False},
                {"option_id": "D", "option_text": "Survey team members about their current productivity challenges and needs", "is_correct": False}
            ],
            "correct_answer_id": "A",
            "difficulty_level": 3,
            "explanation": "Critical thinking requires examining evidence objectively and questioning claims by seeking independent verification and understanding underlying methodologies."
        },
        
        # STRESS MANAGEMENT (Emotional Intelligence)
        {
            "skill_type": "stress_management",
            "skill_name": "Stress Management",
            "scenario_text": "You're managing multiple projects with overlapping deadlines. Team members frequently interrupt you with questions, emails pile up throughout the day, and you often feel like you're constantly switching between tasks without making significant progress on any of them.",
            "question_text": "What strategy would most improve your stress management and productivity?",
            "options": [
                {"option_id": "A", "option_text": "Check emails only at designated times and block focused work periods in your calendar", "is_correct": True},
                {"option_id": "B", "option_text": "Work longer hours to catch up on everything", "is_correct": False},
                {"option_id": "C", "option_text": "Delegate as many tasks as possible to team members", "is_correct": False},
                {"option_id": "D", "option_text": "Use productivity apps to track and optimize your time usage", "is_correct": False}
            ],
            "correct_answer_id": "A",
            "difficulty_level": 2,
            "explanation": "Time blocking and controlling interruptions are fundamental stress management strategies that address the root causes of fragmented attention and overwhelm."
        },
        
        # WRITTEN COMMUNICATION (Communication)
        {
            "skill_type": "written_communication",
            "skill_name": "Written Communication",
            "scenario_text": "You need to email a client about a project delay that will impact their launch timeline. The delay is due to unexpected technical challenges that your team is working to resolve. The client is already frustrated with previous minor delays.",
            "question_text": "How should you structure this communication?",
            "options": [
                {"option_id": "A", "option_text": "Start with the delay announcement, then explain the technical reasons in detail", "is_correct": False},
                {"option_id": "B", "option_text": "Begin by acknowledging the impact, explain the situation clearly, and provide a concrete action plan", "is_correct": True},
                {"option_id": "C", "option_text": "Focus on the technical complexity to help them understand why the delay occurred", "is_correct": False},
                {"option_id": "D", "option_text": "Keep it brief and just state the new timeline without extensive explanations", "is_correct": False}
            ],
            "correct_answer_id": "B",
            "difficulty_level": 3,
            "explanation": "Effective written communication acknowledges impact first, provides clear explanations, and offers concrete solutions to maintain trust."
        },
        
        # NONVERBAL COMMUNICATION (Communication)
        {
            "skill_type": "nonverbal_communication",
            "skill_name": "Nonverbal Communication",
            "scenario_text": "During a client presentation, you notice that while the decision-maker is nodding and seems engaged, their arms are crossed and they keep checking their phone. Other attendees are taking notes but looking at the decision-maker frequently.",
            "question_text": "How should you interpret and respond to these nonverbal cues?",
            "options": [
                {"option_id": "A", "option_text": "Continue with your presentation as planned since they appear to be listening", "is_correct": False},
                {"option_id": "B", "option_text": "Pause and ask if there are any immediate questions or concerns to address", "is_correct": True},
                {"option_id": "C", "option_text": "Speed up your presentation to respect their time constraints", "is_correct": False},
                {"option_id": "D", "option_text": "Ask them directly to put their phone away to focus on the presentation", "is_correct": False}
            ],
            "correct_answer_id": "B",
            "difficulty_level": 3,
            "explanation": "Reading nonverbal cues like defensive posture and distraction signals the need to address underlying concerns before continuing."
        },
        
        # DELEGATION (Leadership)
        {
            "skill_type": "delegation",
            "skill_name": "Delegation",
            "scenario_text": "You have a complex project with multiple components. Your team includes a junior developer eager to take on more responsibility, a senior developer who works well independently, and a mid-level developer who prefers clear guidance. You need to delegate parts of the project effectively.",
            "question_text": "How should you approach delegating tasks to maximize team effectiveness?",
            "options": [
                {"option_id": "A", "option_text": "Give the junior developer simpler tasks and have the senior developer handle complex components", "is_correct": False},
                {"option_id": "B", "option_text": "Match task complexity to each person's experience level while providing appropriate support", "is_correct": True},
                {"option_id": "C", "option_text": "Divide the project equally among all team members regardless of experience", "is_correct": False},
                {"option_id": "D", "option_text": "Let team members choose which components they want to work on", "is_correct": False}
            ],
            "correct_answer_id": "B",
            "difficulty_level": 3,
            "explanation": "Effective delegation considers individual capabilities and provides appropriate support while challenging team members to grow."
        },
        
        # CULTURAL AWARENESS (Teamwork)
        {
            "skill_type": "cultural_awareness",
            "skill_name": "Cultural Awareness",
            "scenario_text": "Your global team includes members from cultures where direct criticism is considered impolite, while others prefer straightforward feedback. During a project review, you need to address performance issues that affect the entire team's success.",
            "question_text": "How do you provide effective feedback while respecting cultural differences?",
            "options": [
                {"option_id": "A", "option_text": "Use the same feedback style for everyone to maintain consistency", "is_correct": False},
                {"option_id": "B", "option_text": "Adapt your communication style to each person's cultural preferences while maintaining clear expectations", "is_correct": True},
                {"option_id": "C", "option_text": "Focus only on positive feedback to avoid cultural misunderstandings", "is_correct": False},
                {"option_id": "D", "option_text": "Ask team members privately how they prefer to receive feedback", "is_correct": False}
            ],
            "correct_answer_id": "B",
            "difficulty_level": 4,
            "explanation": "Cultural awareness means adapting communication styles while ensuring clear expectations and accountability for all team members."
        },
        
        # SELF AWARENESS (Emotional Intelligence)
        {
            "skill_type": "self_awareness",
            "skill_name": "Self Awareness",
            "scenario_text": "You've been feeling increasingly frustrated with a team member who frequently misses deadlines and provides incomplete work. Today, during a team meeting, you found yourself becoming visibly irritated when they asked for an extension on another task.",
            "question_text": "What demonstrates the best self-awareness in this situation?",
            "options": [
                {"option_id": "A", "option_text": "Acknowledge your frustration and suggest discussing workload management privately", "is_correct": True},
                {"option_id": "B", "option_text": "Continue the meeting professionally and address the pattern of delays later", "is_correct": False},
                {"option_id": "C", "option_text": "Express your concerns immediately while emotions are present to show authenticity", "is_correct": False},
                {"option_id": "D", "option_text": "Take a break from the meeting to collect yourself before continuing", "is_correct": False}
            ],
            "correct_answer_id": "A",
            "difficulty_level": 3,
            "explanation": "Self-awareness involves recognizing your emotional state and taking appropriate action that addresses both feelings and underlying issues."
        },
        
        # CREATIVITY (Problem Solving)
        {
            "skill_type": "creativity",
            "skill_name": "Creativity",
            "scenario_text": "Your team has been trying to solve a recurring customer complaint using traditional approaches, but the problem persists. Resources are limited, and management is pressuring for a quick resolution. The usual solutions have only provided temporary fixes.",
            "question_text": "How do you approach this challenge creatively?",
            "options": [
                {"option_id": "A", "option_text": "Brainstorm completely different approaches by reframing the problem from the customer's perspective", "is_correct": True},
                {"option_id": "B", "option_text": "Research how other companies in your industry handle similar issues", "is_correct": False},
                {"option_id": "C", "option_text": "Combine elements from previous solutions to create a more comprehensive approach", "is_correct": False},
                {"option_id": "D", "option_text": "Focus on implementing the most promising traditional solution more thoroughly", "is_correct": False}
            ],
            "correct_answer_id": "A",
            "difficulty_level": 4,
            "explanation": "Creativity involves reframing problems from new perspectives to discover innovative solutions beyond traditional approaches."
        },
        
        # ANALYTICAL THINKING (Problem Solving)
        {
            "skill_type": "analytical_thinking",
            "skill_name": "Analytical Thinking",
            "scenario_text": "Your company's customer satisfaction scores have dropped from 85% to 78% over the last six months. Multiple factors could be contributing: new competitors, product changes, service issues, pricing changes, or market conditions. Management needs a clear understanding of the primary causes.",
            "question_text": "What analytical approach would best identify the main factors affecting satisfaction?",
            "options": [
                {"option_id": "A", "option_text": "Survey customers directly about their satisfaction with different aspects of your service", "is_correct": False},
                {"option_id": "B", "option_text": "Analyze satisfaction data by customer segment, time period, and service touchpoints to identify patterns", "is_correct": True},
                {"option_id": "C", "option_text": "Compare your satisfaction scores with industry benchmarks and competitor data", "is_correct": False},
                {"option_id": "D", "option_text": "Review customer complaints and feedback to identify common themes", "is_correct": False}
            ],
            "correct_answer_id": "B",
            "difficulty_level": 4,
            "explanation": "Analytical thinking requires systematic data segmentation and pattern analysis to identify specific causes rather than general correlations."
        }
    ]
    
    questions = []
    for q_data in questions_data:
        # Create option objects
        options = [
            AssessmentQuestionOption(
                option_id=opt["option_id"],
                option_text=opt["option_text"],
                is_correct=opt["is_correct"]
            )
            for opt in q_data["options"]
        ]
        
        # Create question
        question = AssessmentQuestion(
            skill_type=q_data["skill_type"],
            skill_name=q_data["skill_name"],
            scenario_text=q_data["scenario_text"],
            question_text=q_data["question_text"],
            options=options,
            correct_answer_id=q_data["correct_answer_id"],
            difficulty_level=q_data["difficulty_level"],
            explanation=q_data["explanation"],
            tags=["initial_assessment", q_data["skill_type"]]
        )
        
        questions.append(question)
    
    return questions

async def populate_assessment_questions():
    """Populate the database with assessment questions"""
    try:
        # Connect to MongoDB (adjust connection string as needed)
        client = AsyncIOMotorClient("mongodb://admin:ELTopn4590@3.217.49.154/soft_skills_practice?authSource=admin")
        
        # Initialize Beanie with only Document models
        await init_beanie(
            database=client.soft_skills_practice,  # Use the same database name as in connection string
            document_models=[AssessmentQuestion, InitialAssessment]
        )
        
        print("🔗 Connected to MongoDB")
        
        # Check if questions already exist and delete them
        existing_count = await AssessmentQuestion.count()
        if existing_count > 0:
            print(f"⚠️  Found {existing_count} existing assessment questions")
            print("🗑️  Deleting all existing assessment questions...")
            await AssessmentQuestion.delete_all()
            print("✅ All existing assessment questions deleted")
        
        # Also check and delete any existing assessments
        existing_assessments = await InitialAssessment.count()
        if existing_assessments > 0:
            print(f"⚠️  Found {existing_assessments} existing assessments")
            print("�️  Deleting all existing assessments...")
            await InitialAssessment.delete_all()
            print("✅ All existing assessments deleted")
        
        print("🔄 Creating fresh assessment questions...")
        
        # Create questions
        questions = await create_assessment_questions()
        
        # Insert questions
        inserted_questions = []
        for question in questions:
            try:
                saved_question = await question.insert()
                inserted_questions.append(saved_question)
                print(f"✅ Created question for {question.skill_type}: {question.question_text[:50]}...")
            except Exception as e:
                print(f"❌ Error creating question: {e}")
        
        print(f"\n🎉 Successfully created {len(inserted_questions)} assessment questions!")
        
        # Print summary by skill
        skills_summary = {}
        for q in inserted_questions:
            skill = q.skill_type
            if skill not in skills_summary:
                skills_summary[skill] = 0
            skills_summary[skill] += 1
        
        print("\n📊 Questions by skill:")
        for skill, count in skills_summary.items():
            print(f"  • {skill}: {count} questions")
        
        print("\n✨ Assessment questions database is ready!")
        print("Users can now take initial assessments to identify their soft skills strengths and areas for improvement.")
        
    except Exception as e:
        print(f"❌ Error populating assessment questions: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(populate_assessment_questions())
