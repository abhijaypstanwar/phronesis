import ollama
from typing import List

def _call_ollama(messages: list, model: str = "llama3.2") -> str:
    try:
        client = ollama.Client(host="http://host.docker.internal:11434")
        response = client.chat(model=model, messages=messages)
        return response["message"]["content"]
    except Exception as e:
        err = str(e)
        if "connection" in err.lower() or "refused" in err.lower():
            return "I can't connect to the AI right now. Make sure Ollama is running at http://localhost:11434"
        return f"Something went wrong: {err}"

def course_chat(
    user_message: str,
    course_title: str,
    lesson_contents: List[str],
    enrolled: bool,
    conversation_history: List[dict],
) -> str:
    if enrolled and lesson_contents:
        lessons_text = "\n\n".join(lesson_contents[:4])
        system = f"""You are an expert tutor for the course: "{course_title}".
The student is enrolled. Use this course content to answer their questions:

{lessons_text}

Rules:
- Only answer questions related to this course
- Be clear, educational, and concise
- Use markdown formatting: **bold** for key terms, code blocks with triple backticks for all code examples
- Always show code in proper code blocks with language specified e.g. ```python
- Keep responses under 250 words"""
    else:
        system = f"""You are a helpful assistant for Phronesis learning platform.
The student is asking about "{course_title}" but is not enrolled.
Give a brief 2-3 sentence overview and encourage enrollment.
Keep it under 60 words."""

    messages = [{"role": "system", "content": system}]
    for msg in conversation_history[-6:]:
        messages.append(msg)
    messages.append({"role": "user", "content": user_message})
    return _call_ollama(messages)

def dashboard_chat(
    user_message: str,
    enrolled_courses: List[dict],
    conversation_history: List[dict],
) -> str:
    if enrolled_courses:
        courses_summary = "\n".join([
            f"- {c['title']} ({c.get('percentage', 0)}% complete)"
            for c in enrolled_courses
        ])
        system = f"""You are a helpful learning assistant on Phronesis.

Student's enrolled courses:
{courses_summary}

Rules:
- Help with questions about any of their enrolled courses
- Give general guidance, motivation, and learning tips
- Use markdown: **bold** for key terms, code blocks for any code examples
- Suggest opening a specific course page for deeper help
- Be encouraging, friendly, and concise
- Under 200 words"""
    else:
        system = """You are a helpful assistant on Phronesis learning platform.
The student has not enrolled in any courses yet. Encourage them to browse courses.
Be friendly. Under 60 words."""

    messages = [{"role": "system", "content": system}]
    for msg in conversation_history[-8:]:
        messages.append(msg)
    messages.append({"role": "user", "content": user_message})
    return _call_ollama(messages)