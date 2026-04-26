import streamlit as st
import pandas as pd
from agent import (match_skills,extract_text_from_file)
from question_generator import generate_assessment_questions
from evaluator import evaluate_answers
from learning_plan import generate_learning_plan


def display_skills_as_tags(title, skills, color="#2563eb"):
    st.markdown(f"#### {title}")

    if skills:
        tags_html = """
<div style="
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    align-items: center;
">
"""

        for skill in skills:
            tags_html += f"""
<div style="
    background-color: {color};
    color: white;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 500;
    white-space: nowrap;
    display: inline-block;
">
    {skill}
</div>
"""

        tags_html += "</div>"

        st.markdown(tags_html, unsafe_allow_html=True)

    else:
        st.write("No skills found")

st.set_page_config(
    page_title="SkillSync AI",
    page_icon="🚀",
    layout="centered"
)

st.title("🚀 SkillSync AI")

st.markdown("""
### Welcome Future Achiever 👋

#### I’m your Skill Assessment & Personalized Learning Plan Agent

🔍 Understand your current skill level  
🎯 Compare your profile with job requirements  
📈 Identify missing and weak skills  
🧠 Assess real proficiency through smart questions  
🛠 Build your personalized learning roadmap  
📚 Recommend curated resources + time estimates  
🚀 Suggest adjacent skills for faster career growth  

---

#### Beyond Resume Matching — Real Skill Assessment Starts Here 🚀
""")

# =====================================
# Job Description Section
# =====================================

st.markdown("##### 📄 Job Description")

col1, col2 = st.columns([2, 3])

with col1:
    jd_file = st.file_uploader(
        "Upload File",
        type=["pdf", "txt", "docx", "jpg", "png", "jpeg"],
        key="jd_upload"
    )

with col2:
    jd_text = st.text_area(
        "Paste JD Here",
        height=127,
        key="jd_text"
    )

st.divider()

# =====================================
# Resume Section
# =====================================

st.markdown("##### 📄 Candidate Resume")

col3, col4 = st.columns([2, 3])

with col3:
    resume_file = st.file_uploader(
        "Upload File",
        type=["pdf", "txt", "docx", "jpg", "png", "jpeg"],
        key="resume_upload"
    )

with col4:
    resume_text = st.text_area(
        "Paste Resume Here",
        height=127,
        key="resume_text"
    )

st.divider()

# =====================================
# Session State Initialization
# =====================================

if "results" not in st.session_state:
    st.session_state.results = None

if "experience_level" not in st.session_state:
    st.session_state.experience_level = "Select Experience Level"

if "questions" not in st.session_state:
    st.session_state.questions = []

# =====================================
# Evaluate Button
# =====================================

if st.button("🚀 Evaluate My Skills"):
    if (jd_file or jd_text) and (resume_file or resume_text):

        # Job Description Text
        if jd_text:
            final_jd_text = jd_text
        elif jd_file:
            final_jd_text = extract_text_from_file(jd_file)
        else:
            final_jd_text = ""

        # Resume Text
        if resume_text:
            final_resume_text = resume_text
        elif resume_file:
            final_resume_text = extract_text_from_file(resume_file)
        else:
            final_resume_text = ""

        with st.spinner("Analyzing skills using AI..."):

            results = match_skills(final_jd_text, final_resume_text)

            if not results["jd_skills"] or not results["resume_skills"]:
                st.warning(
                    "⚠ No meaningful skills found. Please upload a better Resume or Job Description."
                )
                st.stop()
            # Save results
            st.session_state.results = results

            # Reset old questions when new evaluation happens
            st.session_state.questions = []

    else:
        st.warning(
            "⚠ Please upload or paste both Job Description and Resume first."
        )

# =====================================
# Show Results After Button Click
# =====================================

if st.session_state.results:

    results = st.session_state.results

    st.success("✅ Skill extraction completed successfully!")

    display_skills_as_tags(
        "📌 Skills in Job Description",
        results["jd_skills"],"#2563eb")

    display_skills_as_tags(
        "📌 Skills in Resume",
        results["resume_skills"],"#7c3aed")

    display_skills_as_tags(
        "✅ Matched Skills",
        results["matched_skills"],"#16a34a")

    display_skills_as_tags(
        "⚠ Missing Skills",
        results["missing_skills"],"#dc2626")

    st.divider()

    # =====================================
    # Experience Level Selection
    # =====================================

    st.markdown("#### 🎯 Required Experience Level for Assessment")

    experience_level = st.selectbox(
        "Choose Experience Level",
        [
            "Select Experience Level",
            "Beginner (0–2 Years)",
            "Intermediate (2–5 Years)",
            "Advanced (5+ Years)"
        ],
        key="experience_level"
    )

    if experience_level != "Select Experience Level":

        st.success(
            f"✅ Thank you! Your selected experience level is: {experience_level}"
        )

        # Generate questions only once
        if not st.session_state.questions:
            with st.spinner("Generating personalized interview questions..."):

                st.session_state.questions = generate_assessment_questions(
                    results["matched_skills"],
                    experience_level
                )

        st.divider()
        st.markdown("#### 🧠 AI Generated Skill Assessment Questions")

        if st.session_state.questions:

            user_answers = []

            for index, item in enumerate(st.session_state.questions, 1):
                st.markdown(
                    f"**Q{index}. ({item['skill']})** {item['question']}"
                )

                answer = st.text_area(
                    "",
                    placeholder="Your Answer Here",
                    key=f"answer_{index}"
                )

                user_answers.append({
                    "skill": item["skill"],
                    "question": item["question"],
                    "answer": answer
                })

            st.divider()

            if st.button("🚀 Submit Answers for Evaluation"):

                # Check if all answers are provided
                all_answered = all(
                    answer["answer"].strip() != ""
                    for answer in user_answers
                )

                if not all_answered:
                    st.warning(
                        "⚠ Please answer all questions before submitting for evaluation."
                    )

                else:
                    with st.spinner("Evaluating your answers using AI..."):

                        evaluation_results = evaluate_answers(
                            user_answers,
                            experience_level
                        )

                    st.markdown("#### 📊 Skill Proficiency Evaluation")

                    # =====================================
                    # Assessment Summary Card
                    # =====================================

                    total_score = 0
                    total_skills = len(evaluation_results)
                    missing_skills_count = len(results["missing_skills"])

                    for item in evaluation_results:
                        total_score += item["score"]

                    overall_score = int(total_score / total_skills) if total_skills > 0 else 0
                    matched_skills_count = len(results["matched_skills"])
                    total_jd_skills = len(results["jd_skills"])

                    match_percentage = int(
                        (matched_skills_count / total_jd_skills) * 100
                        ) if total_jd_skills > 0 else 0

                    # Interview Readiness Logic
                    if overall_score >= 80 and match_percentage >= 80:
                        readiness = "🟢 Strong Candidate"
                    elif overall_score >= 60 and match_percentage >= 60:
                        readiness = "🟡 Promising Candidate"
                    else:
                        readiness = "🔴 Needs Improvement"

                    st.divider()
                    st.markdown("##### 📈 Assessment Summary")

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Overall Score", f"{overall_score}/100")

                    with col2:
                        st.metric("Skills Assessed", total_skills)

                    with col3:
                        st.metric("Missing Skills", missing_skills_count)

                    with col4:
                        with col4:
                            st.markdown("Interview Readiness")
                            st.write(readiness)

                    st.success(
                        f"Assessment Result: {readiness}"
                        )

                    st.divider()

                    if evaluation_results:

                        for item in evaluation_results:
                            score = item["score"]
                            
                            #status Logic
                            if score >= 80:
                                status = "🟢 Strong"
                            elif score >= 60:
                                status = "🟡 Moderate"
                            else:
                                status = "🔴 Needs Improvement"
                            
                            st.markdown(f"#### {item['skill']}")
                            st.markdown(f"##### {status} | Score: {score}/100")

                            # Progress Bar
                            st.progress(score)

                            with st.expander(f"View Detailed Feedback for {item['skill']}"):
                                st.markdown(f"**Feedback:** {item['feedback']}")
                                st.markdown(f"**Improvement Suggestion:** {item['suggestion']}")

                            st.markdown("---")

                        st.divider()
                        st.markdown("#### 📚 Personalized Learning Plan")

                        learning_plan_result = generate_learning_plan(
                            results["missing_skills"],
                            evaluation_results,
                            results["matched_skills"],
                            experience_level
                        )

                        if learning_plan_result["learning_plan"]:

                            for plan in learning_plan_result["learning_plan"]:
                                st.markdown(f"#### 📘 {plan['skill']}")

                                with st.expander(f"View Learning Plan"):

                                    st.markdown("##### 🎯 Focus Area")
                                    st.write(plan["focus_area"])

                                    st.markdown("##### ⏳ Time Estimate")
                                    st.write(plan["time_estimate"])

                                    st.markdown("##### 📚 Recommended Resources")
                                    st.write(", ".join(plan["resources"]))

                                st.markdown("---")
                                
                        if learning_plan_result["adjacent_skills"]:

                            display_skills_as_tags(
                                "🚀 Recommended Adjacent Skills",
                                learning_plan_result["adjacent_skills"], "#f59e0b"
                            )

                    else:
                        st.warning(
                            "⚠ Unable to evaluate answers. Please try again."
                        )

        else:
            st.warning(
                "⚠ Unable to generate questions. Please try again."
            )