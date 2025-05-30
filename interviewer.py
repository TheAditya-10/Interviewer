from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


model = ChatOllama(model="phi3:mini", temperature=0.7, max_tokens=512)
strOutputParser = StrOutputParser()

system_prompt = PromptTemplate( 
    input_variables=["candidate_info", "resume_text", "job_description"],
    template=(
            "You are a professional interviewer going to take interview for the position described below. \n" 
            "You have ask first question, start with ice breaker or intro question based on the following information.\n"
            "Candidate Information:\n{candidate_info}\n"
            "Resume:\n{resume_text}\n"
            "Job Description:\n{job_description}\n\n"
            "Be professional and concise.\n"
            "Start the interview now."
        ),
)
question_prompt = PromptTemplate(
    input_variables=["messages"],
    template=(
            "You are a professional interviewer taking interview \n"
            "Here is the whole chat of the interview untill now: {messages}\n"
            "You have just ask next question."
            "These are the rules you have to follow while asking for a question:\n"
            "Wait for candidate to answer the question before asking the next question.\n"
            "Take the most important topic relevant for a job and based on resume and start easy questions\n"
            "If candidate is answering correctly, gradually increase the difficulty of the next question.\n"
            "If candidate is struggling, ask simpler or clarifying questions.\n"
            "Vary the question types (theory, practical, scenario-based, etc.).\n"
            "Move to next topic when the candidate has demonstrated sufficient knowledge in the current topic or candidate appologised that he/she is unable to answer this question.\n"
            "If candidate is unable to answer a question correctly, ask a related simpler question to help them get back on track. If he/she is fully wrong, go to next topic and sweetly tell him/her that you are wrong\n"
            "Be professional and concise.\n"
            "Start the interview now."
        ),
)

def get_first_question(candidate_info, resume_text, job_description):
    question_chain = system_prompt | model | strOutputParser
    first_question = question_chain.invoke({
        "candidate_info": candidate_info,
        "resume_text": resume_text,
        "job_description": job_description
    })
    messages = [AIMessage(content=first_question)]
    return first_question, messages

def get_next_question(messages):
    interview_chain = question_prompt | model | strOutputParser
    chat_history = ""
    for msg in messages:
        role = "AI" if isinstance(msg, AIMessage) else "Candidate"
        chat_history += f"{role}: {msg.content}\n"
    next_q = interview_chain.invoke({"messages": chat_history})
    messages.append(AIMessage(content=next_q))
    return next_q, messages

def record_answer(messages, answer):
    messages.append(HumanMessage(content=answer))
    return messages

# --- DEMO RUN ---
if __name__ == "__main__":
    candidate_info = "Name: Aditya\nExperience: Fresher"
    resume_text = "Experienced Python developer with expertise in ML, Flask, Deep learning databases."
    job_description = "Looking for a backend developer skilled in Python, Django, ML."

    # Start interview
    question, messages = get_first_question(candidate_info, resume_text, job_description)
    print("AI:", question)

    # Simulate a conversation
    while True:
        answer = input("You: ")
        if answer.strip().lower() == "bye":
            print("Interview ended.")
            break
        messages = record_answer(messages, answer)
        question, messages = get_next_question(messages)
        print("AI:", question)
