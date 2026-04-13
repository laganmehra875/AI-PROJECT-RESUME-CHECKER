from mistralai.client.sdk import Mistral
import json
import os

# ✅ Add your API key properly
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

def analyze_resume(resume_text, user_goal):
    prompt = f"""
You are a Senior software engineer and hiring manager.

Evaluate the resume based on the user's goal.

User_goal: "{user_goal}"

STRICT RULES:
- Extract only relevant skills for this goal
- Remove irrelevant tools
- Identify real gaps
- Generate roadmap only for missing fields
- Make output different based on goal

Return ONLY valid JSON:
{{
  "skills": ["string", "string"],
  "missing_skills": ["string", "string"],
  "roadmap": ["string sentence", "string sentence"],
  "interview_questions": ["string", "string"]
}}

Resume:
{resume_text}
"""

    try:
        response = client.chat.complete(
            model="mistral-small",
            temperature=0.3,
            messages=[
                {"role": "system", "content": "You are a strict hiring manager."},
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content

        # ✅ Clean response (important)
        content = content.strip()

        # If model adds extra text → extract JSON only
        if "{" in content:
            content = content[content.find("{"):content.rfind("}")+1]

        return json.loads(content)

    except Exception as e:
        print(f"Error calling Mistral API: {e}")
        return {"error": str(e)}