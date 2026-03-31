from app.llm import call_llm
import json
import re

def assess_document(text: str):
    try:
        prompt = f"""
        You are a senior Business Analyst.

        Analyze the following document.

        Classify it into:
        - Raw Idea
        - Unstructured Requirements
        - Partial FRD
        - Complete FRD

        Also:
        - Give maturity score (0-100)
        - List missing sections

        Return ONLY JSON:

        {{
            "document_type": "",
            "maturity_score": 0,
            "missing_sections": []
        }}

        Document:
        {text}
        """

        output = call_llm(prompt)

        print("LLM OUTPUT:", output)
        parsed = extract_json(output)
        if parsed:
            return parsed
        else:
            return {"error": "Failed to parse LLM output as JSON", "raw_output": output}

    except Exception as e:
        return {"error": str(e), "raw_output": output}
    
def extract_json(text):
    try:
        match =re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return None
    except:
        return None