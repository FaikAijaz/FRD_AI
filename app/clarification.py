from app.llm import call_llm


def generate_question(context: str, missing_sections: list):
    prompt = f"""
    You are a Senior Business Analyst.

    Based on the following project description:

    {context}

    And missing information areas:

    {missing_sections}

    Ask ONE clear and concise clarification question.

    Do NOT ask multiple questions.
    Do NOT explain anything.
    Only return the question.
    """

    return call_llm(prompt)