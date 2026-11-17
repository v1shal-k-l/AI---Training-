
from app.ai.llm_client import MODEL_NAME, get_llm


llm = get_llm()

response = llm.invoke(
    "Explain the difference between hardware and software issues in an IT helpdesk."
)

print(f"\nAI RESPONSE ({MODEL_NAME}):")
print(response.content)
