import os
import json
from mistralai.client.sdk import Mistral

def analyze_resume(resume_text, user_goal):
    # ✅ Check for API key inside the function for better debugging
    api_key = os.getenv("MISTRAL_API_KEY")
    
    if not api_key or api_key == "your_api_key_here":
        return {"error": "MISTRAL_API_KEY is not set correctly in Render! Go to 'Environment' tab and add it."}
    
    client = Mistral(api_key=api_key)
    
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
        content = content.strip()

        if "{" in content:
            content = content[content.find("{"):content.rfind("}")+1]

        return json.loads(content)

    except Exception as e:
        print(f"Error calling Mistral API: {e}")
        return {"error": f"API Error: {str(e)}"}