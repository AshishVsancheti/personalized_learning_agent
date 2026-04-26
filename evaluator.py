from groq import Groq
import os
from dotenv import load_dotenv
import PyPDF2
from docx import Document
import json

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def evaluate_answers(questions_with_answers, experience_level):
    prompt = f"""
    Return ONLY valid JSON.

    You are an expert interviewer, recruiter, and skill assessment specialist.

    Evaluate the candidate's answers like a real technical interviewer.

    Inputs:
    - Experience Level: {experience_level}
    - Questions + Candidate Answers: {questions_with_answers}

    Evaluation Rules:

    1. Evaluate answer quality based on:
       - correctness
       - conceptual understanding
       - practical thinking
       - depth of knowledge
       - relevance to experience level

    2. For each skill, provide:
       - proficiency score out of 100
       - short feedback
       - improvement suggestion

    3. Be realistic like an actual interviewer

    Return ONLY in this exact JSON format:

    {{
        "evaluations": [
            {{
                "skill": "Python",
                "score": 82,
                "feedback": "Good understanding of Python fundamentals.",
                "suggestion": "Practice advanced concepts like decorators and generators."
            }},
            {{
                "skill": "SQL",
                "score": 68,
                "feedback": "Basic SQL concepts are clear, but advanced query writing is weak.",
                "suggestion": "Focus on joins, subqueries, and window functions."
            }}
        ]
    }}
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                "role": "user",
                "content": prompt
                }
            ],
            temperature=0
        )

        result = response.choices[0].message.content.strip()

    except Exception as e:
        print("Evaluation Error:", e)
        return []

    result = result.replace("```json", "")
    result = result.replace("```python", "")
    result = result.replace("```", "")
    result = result.strip()

    start_index = result.find("{")
    end_index = result.rfind("}") + 1

    if start_index != -1 and end_index != -1:
        result = result[start_index:end_index]

    print("Evaluation Result:", result)

    try:
        evaluation_dict = json.loads(result)
    except:
        evaluation_dict = {
            "evaluations": []
        }

    return evaluation_dict["evaluations"]