# =====================================
# Import Required Libraries
# =====================================

from groq import Groq
import os
from dotenv import load_dotenv
import PyPDF2
from docx import Document
import json

# Load Environment Variables
load_dotenv()

# Create Groq Client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# =====================================
# Function: Generate Personalized Learning Plan
# =====================================

def generate_learning_plan(missing_skills,evaluation_results,matched_skills,experience_level):
    
    # Prompt for AI Learning Plan Generation
    prompt = f"""
    Return ONLY valid JSON.

    You are an expert career mentor, interviewer, and learning path advisor.

    Your task is to create a personalized learning plan for the candidate.

    Inputs:

    - Missing Skills: {missing_skills}
    - Skill Evaluation Results: {evaluation_results}
    - Matched Skills: {matched_skills}
    - Experience Level: {experience_level}

    Instructions:

    1. Identify the most important weak areas and missing skills

    2. If a skill has strong proficiency (80+),
       include it in the learning plan with a light recommendation such as:

       "You are good to go — just keep practicing for interview confidence."

       Do NOT create a heavy improvement roadmap for strong skills.

       Focus detailed learning plans mainly on:
       - missing skills
       - weak skills
       - moderate skills

    3. Create a realistic personalized learning plan focused on:
       - what to learn first
       - what to improve next
       - interview-focused preparation

    4. Suggest adjacent skills the candidate can realistically acquire
       for better career growth

    5. Recommend only famous, trusted, and commonly used learning resources
       based on the candidate’s domain and target role.

       Examples:

       For IT / Software / Data roles:
       - LeetCode
       - HackerRank
       - W3Schools
       - GeeksforGeeks
       - Microsoft Learn
       - DataCamp
       - Kaggle
       - Coursera
       - Udemy
       - well-known technical YouTube educators

       For Sales / Marketing / HR / Business roles:
       - HubSpot Academy
       - LinkedIn Learning
       - Coursera
       - Udemy
       - Google Digital Garage
       - Harvard Business Review
       - Salesforce Trailhead
       - well-known business YouTube educators

       For Core Engineering / Manufacturing roles:
       - NPTEL
       - Coursera
       - Udemy
       - Skill-Lync
       - AutoCAD official learning
       - SolidWorks tutorials
       - MIT OpenCourseWare
       - CNC/CAD/CAM-focused YouTube educators
       - industry-standard technical YouTube educators
    
       Do NOT recommend random unknown platforms.

       Resources must match the candidate’s role and should be practical,
       trusted, and commonly used for interview preparation and career growth.

    6. Provide a realistic time estimate for each skill individually.

        The time estimate must depend on:

        - skill complexity
        - candidate proficiency score
        - missing vs weak skill
        - experience level
        - practical interview readiness

    7. Keep recommendations practical and role-focused

    Return ONLY in this exact JSON format:

    {{
        "learning_plan": [
            {{
                "skill": "Python",
                "focus_area": "Strong fundamentals already present",
                "time_estimate": "2–3 days",
                "resources": [
                    "LeetCode",
                    "GeeksforGeeks",
                    "YouTube: codebasics"
                ],
                "message": "You are good to go — just keep practicing for interview confidence."
            }},
            {{
                "skill": "SQL",
                "focus_area": "Joins, Subqueries, Window Functions",
                "time_estimate": "1 week",
                "resources": [
                    "LeetCode",
                    "W3Schools",
                    "YouTube: Alex The Analyst"
                ],
                "message": "Focus on improving advanced SQL concepts for stronger interview performance."
            }}
            ],
        "adjacent_skills": [
            "Power BI",
            "Tableau",
            "Data Warehousing"
            ]
    }}
    """
    # Call Groq API
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                "role": "user",
                "content": prompt
                }
            ],
            temperature=0.3
        )

        # Raw response from model
        result = response.choices[0].message.content.strip()

    except Exception as e:
        print("Learning Plan Error:", e)
        return {
        "learning_plan": [],
        "adjacent_skills": []
    }

    # Clean Response
    # Remove markdown wrappers like ```json
    result = result.replace("```json", "")
    result = result.replace("```python", "")
    result = result.replace("```", "")
    result = result.strip()

    # Keep Only JSON Part
    start_index = result.find("{")
    end_index = result.rfind("}") + 1

    if start_index != -1 and end_index != -1:
        result = result[start_index:end_index]

    print("Learning Plan Result:", result)

    # Convert JSON String → Python Dictionary
    try:
        learning_plan_dict = json.loads(result)
    except:
        learning_plan_dict = {
            "learning_plan": [],
            "adjacent_skills": []
        }

    # Return Final Learning Plan
    return learning_plan_dict