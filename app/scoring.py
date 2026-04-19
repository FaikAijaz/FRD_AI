from app.llm import call_llm
import json
import re


def extract_json(text):
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return None


def score_frd(frd_text: str):
    try:
        prompt = f"""
        Evaluate the following FRD.

        Return STRICT JSON only. No explanation.
        IMPORTANT:
        - Return ONLY valid JSON
        - Output must start with "{" and end with "}"
        - overall_score MUST be a number between 0 and 100. Never return null.
        Format:

        {{
        "overall_score": 0-100,
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