import json
import os
import re
from dotenv import load_dotenv
from langdetect import detect
from groq import Groq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.models.schemas import AnalysisResponse
from app.services.knowledge_base import retrieve_context  # RAG Integration

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=groq_api_key)

gemini_api_key = os.getenv("GOOGLE_API_KEY")
gemini_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=gemini_api_key)

def get_language(text: str) -> str:
    try:
        return detect(text)
    except:
        return "unknown"

def build_prompt(text: str, lang: str, context: str = "") -> str:
    if lang == "ar":
        return f"""
أنت خبير في تصميم البرامج التدريبية للموظفين والشركات.

المطلوب منك:
- تحليل المستند التدريبي التالي واستخلاص:
  1. ملخص عام للمحتوى (2-3 أسطر).
  2. النقاط التعليمية الأساسية: قائمة بأهم المفاهيم أو المهارات التي يغطيها المحتوى.
  3. الوحدات التدريبية (Modules): 
     - تقسيم المحتوى إلى وحدات منظمة.
     - لكل وحدة: عنوان واضح + وصف مختصر (سطرين).
  4. تقدير الزمن لكل وحدة (بالدقائق) بناءً على كثافة المعلومات وتعقيدها.
  5. إحصائيات المستند:
     - عدد الصفحات.
     - نسبة المحتوى المفيد (تقدير تقريبي بين 0 و 1).
     - عدد النقاط التعليمية.

إذا احتجت سياق إضافي، هذه بعض المعلومات:
{context}

أرجو أن يكون الرد فقط بصيغة JSON صحيحة بهذا الشكل:
{{
  "summary": "ملخص المحتوى",
  "key_points": ["نقطة ١", "نقطة ٢", "..."],
  "training_modules": [
    {{"title": "وحدة ١", "description": "وصف مختصر", "estimated_minutes": 30}},
    {{"title": "وحدة ٢", "description": "وصف مختصر", "estimated_minutes": 45}}
  ],
  "num_pages": عدد الصفحات (عدد صحيح),
  "useful_text_ratio": نسبة المحتوى المفيد (رقم عشري بين 0 و 1),
  "num_key_points": عدد النقاط الأساسية (عدد صحيح)
}}

المستند:
{text}
"""
    else:
        return f"""
You are an expert corporate instructional designer.

Please:
- Analyze the following training document and extract:
  1. A concise summary (2-3 sentences).
  2. Key learning points: A list of core concepts or skills covered.
  3. Training modules:
     - Divide the content into organized modules.
     - For each module: provide a clear title + a brief description (2 lines).
  4. Estimate duration (in minutes) for each module based on content density and complexity.
  5. Document statistics:
     - Number of pages.
     - Useful text ratio (between 0 and 1).
     - Number of key points.

If needed, here is additional context from external sources:
{context}

Respond only with valid JSON in this format:
{{
  "summary": "string",
  "key_points": ["point1", "point2", "..."],
  "training_modules": [
    {{"title": "module1", "description": "brief description", "estimated_minutes": 30}},
    {{"title": "module2", "description": "brief description", "estimated_minutes": 45}}
  ],
  "num_pages": integer,
  "useful_text_ratio": float (between 0 and 1),
  "num_key_points": integer
}}

Document:
{text}
"""

def analyze_with_groq(prompt: str) -> dict:
    response = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=2048,
    )
    if not response.choices or not hasattr(response.choices[0], "message"):
        raise RuntimeError("Groq LLM response is empty or malformed.")
    raw_content = response.choices[0].message.content
    print("\nGroq LLM Raw Output:\n", raw_content)
    json_match = re.search(r"\{.*\}", raw_content, re.DOTALL)
    if not json_match:
        raise RuntimeError("No valid JSON block found in Groq response.")
    return json.loads(json_match.group(0))

def analyze_with_gemini(text: str, num_pages: int, useful_ratio: float, context: str = "") -> dict:
    prompt = PromptTemplate.from_template("""
Analyze the following training document and return JSON:

{{
  "summary": "...",
  "key_points": [...],
  "training_modules": [
    {{"title": "...", "description": "...", "estimated_minutes": 30 }}
  ],
  "num_pages": {num_pages},
  "useful_text_ratio": {useful_ratio},
  "num_key_points": ...
}}

External Context:
{context}

Document:
{text}
""")
    parser = JsonOutputParser()
    chain = prompt | gemini_llm | parser
    return chain.invoke({
        "text": text,
        "num_pages": num_pages,
        "useful_ratio": useful_ratio,
        "context": context
    })

def analyze_document(text: str, num_pages: int, useful_ratio: float, provider="groq") -> AnalysisResponse:
    lang = get_language(text)
    context = retrieve_context(text)
    prompt = build_prompt(text, lang, context)

    if provider == "gemini":
        result = analyze_with_gemini(text, num_pages, useful_ratio, context)
    else:
        result = analyze_with_groq(prompt)

    return AnalysisResponse(**result)
