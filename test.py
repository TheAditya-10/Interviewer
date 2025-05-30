from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

model = OllamaLLM(model="phi3:mini")

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
candidate_skills = ['Python', 'GenAI', 'MySQL', 'Flask', 'React', 'Pandas', 'Scikit-learn', 'Matplotlib']
job_skills = ['Python', 'SQL', 'Flask']
chain = prompt | model | StrOutputParser()
result = chain.invoke({
    "candidate_skills": candidate_skills,
    "job_skills": job_skills
})
print(result)  # Output the ordered skills