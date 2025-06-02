from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)
jsonparser = JsonOutputParser()

def get_skill_order(candidate_skills, job_skills):

    prompt = PromptTemplate(
        input_variables=["candidate_skills", "job_skills"],
        template=(
            "Given the following skills that are required for this job: {job_skills}\n"
            "And the following are the skills that candidate applying for job has: {candidate_skills}\n"
            "Return an ordered JSON list (array) of the job skills that are present in candidate also."
            "Judge skills on the basis of domains like MySQL, SQL, MongoDB, DBMS are all of same type(Domain) of skills which are similar, so if job requirement have that particular domain related skill and cadidate also have particular domain related skill then add an General term of that domain (here ex DBMS or SQL) into the list\n"
            "If the name exactly matches in both the list then add it directly, match atleast 3 skills.\n"
            "order that list by best fit or relevance for the job. Try to include as many skills that could be matched by from candidate. "
            "Return only a JSON array, nothing else."
            "Do not include any reasoning, markdown, code block, or extra text. Just list of similar type of skills in JSON format.\n"
        ),
    )
    chain = prompt | model | jsonparser
    result = chain.invoke({
        "candidate_skills": candidate_skills,
        "job_skills": job_skills
    })
    return result