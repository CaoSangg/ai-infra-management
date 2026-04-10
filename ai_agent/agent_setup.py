# Cấu hình agent, setup 2 model
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")

# Agent Chính: Gemini 3.1 Pro
main_agent = ChatGoogleGenerativeAI(
    model="gemini-3.1-pro-preview",
    google_api_key=google_api_key,
    temperature=0.1,
)

# Agent Phụ: Gemini 3 Flash
sub_agent = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    google_api_key=google_api_key,
    temperature=0.1,
)

print("Khởi tạo các AI Model thành công:")
print(f"- Agent chính: {main_agent.model}")
print(f"- Agent phụ: {sub_agent.model}")
