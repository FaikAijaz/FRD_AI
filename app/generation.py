from app.llm import call_llm
import json
import re

def extract_json(text):
    try:
        data = json.loads(text)

        # 🔥 Fix: if incomplete JSON, try to auto-close
        if isinstance(data, dict):
            return data

    except:
        pass

    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            json_str = match.group()

            # 🔥 Fix: auto-balance braces
            open_braces = json_str.count("{")
            close_braces = json_str.count("}")

            if close_braces < open_braces:
                json_str += "}" * (open_braces - close_braces)

            return json.loads(json_str)
    except Exception as e:
        print("JSON parsing error:", e)

    return None


def generate_frd(context: str, answers: list):
    try:
        combined_input = context + "\n" +"\n".join(answers)

        prompt = f"""
        You are a Senior Business Analyst.

        Generate a complete FRD in STRICT JSON format.

        DO NOT write anything outside JSON.
        DO NOT add explanations.
        ONLY return valid JSON.

        IMPORTANT:
        - Output must be valid JSON (parsable by json.loads)
        - No trailing commas
        - No text outside JSON
        - Use proper JSON structure
        - functional_requirements MUST be a JSON array of objects. Do NOT output multiple standalone JSON objects.
        = Before returning, validate that the JSON is syntactically correct.
        Format:

        {{
        "frd_text": "string",
        "sections": {{
            "overview": "string",
            "objectives": "string",
            "functional_requirements": [
            {{
                "id": "1",
                "description": "string"
            }}
            ],
            "non_functional_requirements": [
            {{
                "id": "1",
                "description": "string"
            }}
            ]
        }}
        }}

        Context:
        {combined_input}
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