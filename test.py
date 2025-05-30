from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key="AIzaSyCil3yELy5_mHhdCB4sOjsrVQXYBUha3Po")

result = model.invoke("List the top 5 skills needed for a data scientist, ordered by importance.")
print(result.content)  