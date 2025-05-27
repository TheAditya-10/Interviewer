from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="phi3:mini")
response = llm.invoke("Explain polymorphism.")
print(response)
