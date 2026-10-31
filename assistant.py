import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# ---------- Config ----------
load_dotenv()
MODELS = [m.strip() for m in os.getenv("GEMINI_MODELS", "").split(",") if m.strip()]
if not MODELS or not os.getenv("GOOGLE_API_KEY"):
    sys.exit("Set GOOGLE_API_KEY and GEMINI_MODELS in .env")

OUT = Path("outputs")
OUT.mkdir(exist_ok=True)

# ---------- LLM (first model, then fallbacks) ----------
llms = [ChatGoogleGenerativeAI(model=m, temperature=0, max_retries=2) for m in MODELS]
llm = llms[0].with_fallbacks(llms[1:])
parser = StrOutputParser()


# ---------- Chains ----------
def make_chain(system: str, human: str):
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
    return prompt | llm | parser


generate = make_chain(
    "You are a senior Python developer. Return only code in a single python block.",
    "Write Python code for: {task}",
)
review = make_chain(
    "You are a strict code reviewer. List bugs, style issues and improvements, most severe first.",
    "Review this code:\n{code}",
)
write_tests = make_chain(
    "You are a test engineer. Write pytest tests. Return only code.",
    "Write pytest tests for this code (it lives in generated.py):\n{code}",
)


# ---------- Helpers ----------
def strip_fences(text: str) -> str:
    return "\n".join(l for l in text.splitlines() if not l.strip().startswith("```"))


# ---------- Workflow ----------
def run(task: str) -> None:
    code = strip_fences(generate.invoke({"task": task}))
    (OUT / "generated.py").write_text(code, encoding="utf-8")

    (OUT / "review.md").write_text(review.invoke({"code": code}), encoding="utf-8")

    tests = strip_fences(write_tests.invoke({"code": code}))
    (OUT / "test_generated.py").write_text(tests, encoding="utf-8")
    print("Saved generated.py, review.md, test_generated.py to outputs/")


if __name__ == "__main__":
    run(" ".join(sys.argv[1:]) or "a function that checks if a string is a palindrome")