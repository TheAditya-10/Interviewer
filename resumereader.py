from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dbmodel import Candidate, db, ExperienceLevel
from app import app

# Load environment variables
load_dotenv()

# Initialize language model
llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.2",
    temperature=0,
    max_new_tokens=512,
)
model = ChatHuggingFace(llm=llm)

# Load resume PDF
loader = PyPDFLoader('Aditya_Pratap_Resume.pdf')
docs = loader.load()

# Set up output parser
jsonparser = JsonOutputParser()

# Create prompt template
resume_prompt = PromptTemplate(
    input_variables=["resume_text"],
    template=(
        "Given the following resume text:\n\n"
        "{resume_text}\n\n"
        "Extract and list all of the following information:\n"
        "- Skills - None (Default)\n"
        "- Soft skills- None (Default) : Extract the soft skills from overall resume\n"
        "- Highest qualification (max_qualification)\n"
        "- Achievements\n"
        "- Experience (Intern, Fresher (Default), Intermediate, Expert)\n"
        "Please provide the information in a structured format."
        "\n{format_instructions}\n"
        "Return ONLY a valid JSON object, with all property names and string values in double quotes, and NO trailing commas."
    ),
    partial_variables={'format_instructions': jsonparser.get_format_instructions()}
)

# Format prompt and get response
chain = resume_prompt | model | jsonparser
candidate_data = chain.invoke({"resume_text": docs[0].page_content})
print(candidate_data)
with app.app_context():
    candidate = Candidate(
        skills=candidate_data['skills'],
        soft_skills=candidate_data['soft_skills'],
        achievements=candidate_data['achievements'],
        experience=ExperienceLevel[candidate_data['experience'].replace(" ", "")],
        max_qualification=candidate_data['max_qualification']
    )
    db.session.add(candidate)
    db.session.commit()
    print(f"Candidate added with ID: {candidate.C_id}")