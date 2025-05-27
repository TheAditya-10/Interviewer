from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_ollama import OllamaLLM

# Load environment variables
load_dotenv()

model = OllamaLLM(model="phi3:mini", temperature=0)

def extract_candidate_data(pdf_path):
    loader = PyPDFLoader(pdf_path)
    resume = loader.load()
    jsonparser = JsonOutputParser()
    resume_prompt = PromptTemplate(
        input_variables=["resume_text"],
        template=(
                "Given the following resume:\n\n"
                "{resume_text}\n\n"
                "Extract ONLY the following information as a flat JSON object:\n"
                "- name: string\n"
                "- dob: string (YYYY-MM-DD) Default - 2000-01-01\n"
                "- skills: a list of strings\n"
                "- soft_skills: a list of strings\n"
                "- max_qualification: a string (highest degree or qualification only)\n"
                "- achievements: a list of strings\n"
                "- experience: one of 'Fresher'(Default), 'Intermediate', or 'Expert' (as a string)\n"
                "Return ONLY a valid JSON object, with all property names and string values in double quotes, and NO trailing commas. "
                "Do not include any markdown, code block, or extra text.\n"
                "Example:\n"
                "[\n"
                '  "name": "Shivya Singh"\n'
                '  "dob": "2006-02-11"\n'
                '  "skills": ["Python", "SQL"],\n'
                '  "soft_skills": ["communication", "teamwork"],\n'
                '  "max_qualification": "Bachelor\'s Degree in Computer Science",\n'
                '  "achievements": ["Won coding competition"],\n'
                '  "experience": "Fresher"\n'
                "]\n"
            ),
    )
    chain = resume_prompt | model | jsonparser
    candidate_data = chain.invoke({"resume_text": resume[0].page_content})
    return candidate_data

def get_skill_order(candidate_skills, job_skills):

    prompt = PromptTemplate(
        input_variables=["candidate_skills", "job_skills"],
        template=(
            "Given the following candidate skills: {candidate_skills}\n"
            "And the following job required skills: {job_skills}\n"
            "Return an ordered JSON list (array) of the skills that match between candidate and job, "
            "ordered by best fit or relevance for the job. Only include skills present in both lists. "
            "Return only a JSON array, nothing else."
        ),
    )
    chain = prompt | model | StrOutputParser()
    result = chain.invoke({
        "candidate_skills": candidate_skills,
        "job_skills": job_skills
    })
    import json
    try:
        ordered_skills = json.loads(result)
    except Exception:
        ordered_skills = ['Nothing found']
    return ordered_skills


