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


def generate_frd(context: str, answers: list):
    try:
        combined_input = context + "\n".join(answers)

        prompt = f"""
        You are a Senior Business Analyst.

        Based on the following project details:

        {combined_input}

        Generate a complete Functional Requirement Document (FRD).

        Return ONLY JSON in this format:

        {{
          "frd_text": "full readable document",

          "sections": {{
            "overview": "",
            "objectives": "",
            "stakeholders": "",
            "functional_requirements": [],
            "non_functional_requirements": [],
            "user_stories": [],
            "assumptions": [],
            "risks": []
          }}
        }}
        """

        output = call_llm(prompt)

        print("FRD RAW OUTPUT:", output)

        parsed = extract_json(output)

        if parsed:
            return parsed
        else:
            return {
                "error": "Failed to parse FRD JSON",
                "raw_output": output
            }

    except Exception as e:
        return {"error": str(e)}