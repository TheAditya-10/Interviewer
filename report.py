from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)
strOutputParser = StrOutputParser()

def generate_report(messages, job_skills, duration):
    prompt = PromptTemplate(
        input_variables=["messages", "job_skills", "duration"],
        template=(
            "You are an expert interviewer. Given the following interview chat transcript:\n"
            "{messages}\n\n"
            "And the following required job skills:\n"
            "{job_skills}\n\n"
            "And the duration of the interview in minutes:\n"
            "{duration}\n\n"
            "Generate a detailed report of the conducted interview. The report should include:\n"
            "- An overview of the candidate's performance\n"
            "- Strengths and weaknesses observed during the interview\n"
            "- How well the candidate's responses align with the required job skills\n"
            "- Any notable achievements or red flags\n"
            "- How the candidate's soft skills were demonstrated\n"
            "- How much core knowledge was demonstrated\n"
            "- Any specific examples or quotes from the interview that are very corelated with job that illustrate the candidate's abilities\n"
            "- A summary recommendation (e.g., proceed to next round, needs improvement, etc.)\n\n"
            "- This is a {duration} minute interview, so consider the time taken for responses.\n\n"

        ),
    )
    chain = prompt | model | strOutputParser
    result = chain.invoke({
        "messages": messages,
        "job_skills": job_skills,
        "duration": duration
    })
    return result

def score_report(report):
    prompt = PromptTemplate(
        input_variables=["report"],
        template=(
            "You are an expert interviewer. Given the following interview report\n"
            "{report}\n\n"
            "Score the candidate's performance on a scale of 1 to 100\n"
            "Based on their responses and alignment with the required job skills.\n"
            "Consider the following criteria:\n"
            "- Clarity and relevance of responses\n"
            "- Depth of knowledge and understanding\n"
            "- Alignment with job requirements\n"
            "- Overall impression and professionalism\n"
            "Provide a single integer score without any additional text or explanation."
        ),
    )
    chain = prompt | model | strOutputParser
    result = chain.invoke({
        "report": report
    })
    return int(result) if result.isdigit() else None