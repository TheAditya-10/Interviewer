from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv

load_dotenv()
llm = HuggingFaceEndpoint(
    repo_id="HuggingFaceH4/zephyr-7b-beta",
    temperature=0.5,
    max_new_tokens=512,
)
model = ChatHuggingFace(llm=llm)

print(model.invoke("What is the capital of India?").content)