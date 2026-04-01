from app.llm import call_llm
import json
import re


def extract_json(text):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return None
    except:
        return None


def score_frd(frd_text: str):
    try:
        prompt = f"""
        You are a Senior IT Business Analyst and Quality Auditor.

        Evaluate the following FRD based on:

        1. Clarity
        2. Completeness
        3. Testability
        4. Non-functional requirement coverage
        5. Risk coverage
        6. Ambiguity (lower ambiguity = higher score)

        Return ONLY JSON in this format:

        {{
          "overall_score": 0,
          "category_scores": {{
            "clarity": 0,
            "completeness": 0,
            "testability": 0,
            "nfr_coverage": 0,
            "risk_coverage": 0,
            "ambiguity": 0
          }},
          "strengths": [],
          "improvements": []
        }}

        FRD:
        {frd_text}
        """

        output = call_llm(prompt)

        print("SCORING RAW OUTPUT:", output)

        parsed = extract_json(output)

        if parsed:
            return parsed
        else:
            return {
                "error": "Failed to parse scoring JSON",
                "raw_output": output
            }

    except Exception as e:
        return {"error": str(e)}