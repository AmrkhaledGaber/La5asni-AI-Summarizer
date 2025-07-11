from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import os
from dotenv import load_dotenv
import json

load_dotenv()

gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",  # or "gemini-1.0-pro"
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

def refine_content(original_json: dict, instruction: str) -> dict:
    prompt = PromptTemplate.from_template("""
You are a helpful AI assistant. You are given a training analysis JSON and a user refinement instruction.

Refinement Instruction:
{instruction}

Original JSON:
{original_json}

Now return the updated JSON ONLY with the modifications, using the same structure exactly:
""")

    parser = JsonOutputParser()
    chain = prompt | gemini_llm | parser

    try:
        return chain.invoke({
            "original_json": json.dumps(original_json),
            "instruction": instruction
        })
    except Exception as e:
        print("Gemini refinement failed:", e)
        return original_json
