import google.generativeai as genai
from app.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")


def generate_study_plan(
    course_title: str,
    course_description: str,
    lessons: list[dict],
    completed_lesson_ids: list[str],
    target_date: str,
    student_name: str,
) -> str:
    """
    Calls Gemini to generate a personalised day-by-day study plan.
    Returns the plan as a markdown string.
    """

    # build lesson list for the prompt
    lesson_lines = []
    for l in lessons:
        status = "✓ completed" if l["id"] in completed_lesson_ids else "pending"
        lesson_lines.append(
            f"  - Lesson {l['order']}: {l['title']} ({l.get('duration_min') or 15} min) [{status}]"
        )
    lessons_text = "\n".join(lesson_lines)

    pending_count = len([l for l in lessons if l["id"] not in completed_lesson_ids])

    prompt = f"""
You are an expert learning coach. Generate a personalised, realistic day-by-day study plan.

Student: {student_name}
Course: {course_title}
Description: {course_description or "A structured learning course."}
Target completion date: {target_date}

Lessons in this course:
{lessons_text}

Pending lessons remaining: {pending_count}

Rules:
1. Only include PENDING lessons — skip already completed ones.
2. Assign 1-2 lessons per study day depending on lesson duration.
3. Include rest days (every 3-4 days) for retention.
4. Add a short motivational tip for each study day.
5. End with a brief summary and encouragement.
6. Use this exact format for each day:

📅 Day [N] — [Date e.g. "Mon, Jul 7"]
  📖 [Lesson title] ([duration] min)
  💡 Tip: [one practical study tip for this lesson]

Keep the plan concise, friendly, and achievable.
Start the plan immediately — no preamble or explanation.
"""

    response = model.generate_content(prompt)
    return response.text