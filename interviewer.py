from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_ollama import ChatOllama  # <-- Use ChatOllama

# Load environment variables if needed

chat = ChatOllama(model="phi3:mini", temperature=0.7)
domain = "software engineering"

system_message = SystemMessage(
    content=f"You are an interviewer. Ask the user one {domain} interview question at a time. Wait for their answer before asking the next question."
)

messages = [system_message]

print("Interview started. Type your answers below (type 'bye' to end):")

while True:
    response = chat(messages)
    question = response.content
    print(f"Interviewer: {question}")

    user_answer = input("You: ")
    if user_answer.strip().lower() == "bye":
        print("Interview ended.")
        break
    messages.append(AIMessage(content=question))
    messages.append(HumanMessage(content=user_answer))
