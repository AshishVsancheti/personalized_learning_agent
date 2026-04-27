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
# Function: Generate Assessment Questions
# =====================================

def generate_assessment_questions(matched_skills, experience_level):

    # Prompt for AI Question Generation
    prompt = f"""
    Return ONLY valid JSON.

    You are an expert interviewer and hiring manager.

    Your task is to generate realistic interview assessment questions.

    Inputs:
    - Matched Skills: {matched_skills}
    - Experience Level: {experience_level}

    Strict Rules:

    1. Generate questions ONLY for matched skills

    2. For TECHNICAL skills (Python, SQL, Power BI, Excel, Machine Learning,
       Data Analysis, Java, C++, Tableau, Statistics, etc.)

       MUST generate minimum 4 to 5 questions per skill

       Questions must include:
       - conceptual understanding
       - coding/practical implementation
       - SQL/database problem solving where relevant
       - scenario-based real-world problem
       - optimization/debugging thinking where relevant

       Coding/practical questions are COMPULSORY for technical skills

    3. For NON-TECHNICAL skills (Communication, Sales, HR, Marketing, etc.)

       MUST generate minimum 3 questions per skill

       Questions should include:
       - conceptual understanding
       - practical work situations
       - scenario-based decision making

    4. Difficulty must depend on experience level:

       Beginner → basic/fundamental

       Intermediate → moderate real-world practical questions

       Advanced → deep practical + scenario-heavy interview questions

    5. Questions should feel like real interview questions

    6. Do NOT mention labels like Theory, Practical, Coding, etc.

       Return only natural interview questions

    Return ONLY in this exact JSON format:

    {{
        "questions": [
            {{
                "skill": "Python",
                "question": "What is the difference between list and tuple in Python?"
            }},
            {{
                "skill": "Python",
                "question": "Write a Python function to reverse a string."
            }},
            {{
                "skill": "SQL",
                "question": "Write a SQL query to find the second highest salary."
            }}
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
            temperature=0.7
        )

        # Raw response from model
        result = response.choices[0].message.content.strip()

    except Exception as e:
        print("Question Generation Error:", e)
        return []
    
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

    print("Generated Questions:", result)

    # Convert JSON String → Python Dictionary
    try:
        questions_dict = json.loads(result)
    except:
        questions_dict = {
            "questions": []
        }

    # Return Final Questions List
    return questions_dict["questions"]