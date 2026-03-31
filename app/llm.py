import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # default local

# OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def call_llm(prompt: str):
    if LLM_PROVIDER == "openai":
        return call_openai(prompt)
    else:
        return call_ollama(prompt)


# -----------------------------
# OpenAI
# -----------------------------
def call_openai(prompt: str):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"ERROR: {str(e)}"


# -----------------------------
# Ollama (Local)
# -----------------------------
def call_ollama(prompt: str):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
        )
        data = response.json()
        print("OLLAMA DATA:", data)
        return data.get("response", "")

    except Exception as e:
        return f"ERROR: {str(e)}"