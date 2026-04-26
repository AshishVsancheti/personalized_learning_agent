from groq import Groq
import os
from dotenv import load_dotenv
import PyPDF2
from docx import Document
import json

def extract_text_from_file(uploaded_file):
    file_type = uploaded_file.name.split(".")[-1].lower()

    if file_type == "txt":
        return uploaded_file.read().decode("utf-8")

    elif file_type == "pdf":
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""

        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"

        return text

    elif file_type == "docx":
        doc = Document(uploaded_file)
        text = ""

        for para in doc.paragraphs:
            text += para.text + "\n"

        return text

    else:
        return ""


load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def extract_skills(text, source_type="Job Description"):
    prompt = f"""
    You are an expert recruiter and hiring manager.

    Extract only the strong professional and technical skills from the following {source_type}.

    Important Rules:

    - Prioritize skills from Skills section, Technical Skills section, Certifications, and proven Experience
    - Consider project skills only if they clearly show strong practical proficiency
    - Ignore weak mentions or casual mentions inside project descriptions
    - Ignore generic words like hardworking, good learner, dedicated, etc.
    - Avoid extracting tools/skills mentioned only once without strong relevance
    - Return only meaningful skills useful for job matching

    Return only a clean Python list.

    Example:
        ["Python", "SQL", "Machine Learning", "Communication"]

    Text:
    {text}
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

        return response.choices[0].message.content
    except Exception as e:
        print("Groq API Error:", e)
        return ""

def match_skills(jd_text, resume_text):
    jd_skills = extract_skills(jd_text, "Job Description")
    resume_skills = extract_skills(resume_text, "Resume")

    prompt = f"""
        Return ONLY valid JSON.

        You are an expert recruiter and skill assessment specialist.

        Compare these two skill lists and identify:

        1. matched_skills
        2. missing_skills

        Important Rules:

        - Treat same meaning skills as matched
        - Treat equivalent professional terms as matched
        - Treat parent-child related skills as matched when logically appropriate
        - Treat strongly related domain skills as matched if they represent practical proficiency

        Examples:

        Communication = Communication Skills
        CRM = Client Relationship Management
        Artificial Intelligence = Machine Learning
        Machine Learning = Deep Learning (if role relevance supports it)
        Sales = Business Development
        SQL = Database Management
        Python = Python Programming

        Do NOT be too strict with exact wording.

        Return ONLY in this exact JSON format:

        {{
            "matched_skills": ["skill1", "skill2"],
            "missing_skills": ["skill3", "skill4"]
        }}
        Job Description Skills:
        {jd_skills}

        Resume Skills:
        {resume_skills}
    """

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

    comparison_result = response.choices[0].message.content.strip()
    comparison_result = comparison_result.replace("```json", "")
    comparison_result = comparison_result.replace("```python", "")
    comparison_result = comparison_result.replace("```", "")
    comparison_result = comparison_result.strip()

    # Keep only JSON object part
    start_index = comparison_result.find("{")
    end_index = comparison_result.rfind("}") + 1

    if start_index != -1 and end_index != -1:
        comparison_result = comparison_result[start_index:end_index]

    print("Cleaned Groq Response:", comparison_result)

    try:
        comparison_dict = json.loads(comparison_result)
    except:
        comparison_dict = {
            "matched_skills": [],
            "missing_skills": []
        }

    return {
        "jd_skills": eval(jd_skills) if jd_skills else [],
        "resume_skills": eval(resume_skills) if resume_skills else [],
        "matched_skills": comparison_dict["matched_skills"],
        "missing_skills": comparison_dict["missing_skills"]
    }


