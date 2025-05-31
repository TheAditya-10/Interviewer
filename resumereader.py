from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
jsonparser = JsonOutputParser()

def extract_candidate_data(pdf_path):
    loader = PyPDFLoader(pdf_path)
    resume = loader.load()
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
                "Do not include any reasoning, markdown, code block, or extra text.\n"
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




