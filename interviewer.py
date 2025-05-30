from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


model = ChatOllama(model="phi3:mini", temperature=0.7, max_tokens=512)
strOutputParser = StrOutputParser()

system_prompt = PromptTemplate( 
    input_variables=["candidate_info", "job_info", "interview_info"],
    template=(
            "You are a professional interviewer bot going to take interview for the position described below. \n" 
            "Candidate responses will be going to add into chat history one by one \n"
            "You have ask first question, start with ice breaker or intro question based on the following information.\n"
            "Candidate Information:\n{candidate_info}\n"
            "Job Information:\n{job_info}\n"
            "List of skills that matches in the candidate resume which are required for the job role:\n{interview_info}\n\n"
            "Be professional and concise.\n"
            "Start the interview now."
        ),
)
question_prompt = PromptTemplate(
    input_variables=["messages", "interview_info"],
    template=(
            "You are a professional interviewer taking interview \n"
            "Just to keep you remind these are the List of skills that matches in the candidate resume which are required for the job role:\n{interview_info}\n \n"
            "Here is the whole chat of the interview untill now: {messages}\n"
            "You have just ask next question."
            "These are the rules you have to take care while asking for next question or while analysing the responses:\n"
            "- Wait for candidate to answer the question before asuuming anything or asking the next question.\n"
            "- Take the most important topic relevant for a job and based on resume and start easy questions\n"
            "- If candidate is answering correctly, gradually increase the difficulty of the next question.\n"
            "- If candidate is struggling, ask simpler or clarifying questions.\n"
            "- Vary the question types (theory, practical, scenario-based, etc.).\n"
            "- Move to next topic when the candidate has demonstrated sufficient knowledge in the current topic or candidate appologised that he/she is unable to answer this question.\n"
            "- If candidate is unable to answer a question correctly, ask a related simpler question to help them get back on track. If he/she is fully wrong, go to next topic and sweetly tell him/her that you are wrong\n"
            "Be professional and concise.\n"
            "Start the interview now."
        ),
)

def get_first_question(candidate_info, job_info, interview_info):
    question_chain = system_prompt | model | strOutputParser
    first_question = question_chain.invoke({
        "candidate_info": candidate_info,
        "job_info": job_info,
        "interview_info": interview_info
    })
    messages = [AIMessage(content=first_question)]
    return first_question, messages

def get_next_question(messages, interview_info):
    interview_chain = question_prompt | model | strOutputParser
    chat_history = ""
    for msg in messages:
        role = "AI" if isinstance(msg, AIMessage) else "Candidate"
        chat_history += f"{role}: {msg.content}\n"
    next_q = interview_chain.invoke({"messages": chat_history, "interview_info": interview_info})
    messages.append(AIMessage(content=next_q))
    return next_q, messages

def record_answer(messages, answer):
    messages.append(HumanMessage(content=answer))
    return messages


