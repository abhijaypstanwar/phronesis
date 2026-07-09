"""
Rule-based study plan generator.
No AI API required — calculates a smart schedule from lesson data and target date.
"""
from datetime import date, timedelta
from typing import List
from dataclasses import dataclass

@dataclass
class LessonInfo:
    id: str
    order: int
    title: str
    duration_min: int

def generate_study_plan(
    course_title: str,
    lessons: List[LessonInfo],
    completed_ids: List[str],
    target_date: str,
    student_name: str,
) -> str:
    pending = [l for l in lessons if l.id not in completed_ids]

    if not pending:
        return f"🎉 Congratulations {student_name}! You have already completed all lessons in **{course_title}**. Nothing left to study!"

    try:
        target = date.fromisoformat(target_date)
    except ValueError:
        return "⚠️ Invalid target date provided."

    today      = date.today()
    days_left  = (target - today).days

    if days_left <= 0:
        return f"⚠️ Your target date has already passed. Please choose a future date."

    # ── Calculate schedule ──
    # Add rest days every 4 study days
    # Distribute lessons evenly with max 2 per day
    total_pending  = len(pending)
    max_per_day    = 2
    min_study_days = (total_pending + max_per_day - 1) // max_per_day

    if days_left < min_study_days:
        note = f"⚡ **Ambitious plan!** You have {total_pending} lessons to cover in {days_left} days — that's intensive but doable!\n\n"
    elif days_left > total_pending * 3:
        note = f"😊 You have plenty of time — {days_left} days for {total_pending} lessons. This is a relaxed pace.\n\n"
    else:
        note = f"📈 Great balance — {total_pending} lessons over {days_left} days.\n\n"

    lines = [
        f"📅 **Study Plan — {course_title}**",
        f"👤 Student: {student_name}",
        f"🎯 Target: Complete by {target.strftime('%B %d, %Y')}",
        f"📚 Lessons remaining: {total_pending}",
        f"⏰ Days available: {days_left}",
        "",
        "─" * 45,
        "",
        note.strip(),
        "",
    ]

    # Assign lessons to study days
    study_day   = 0
    lesson_idx  = 0
    current_day = today

    tips = [
        "Read through once, then summarise in your own words.",
        "Take short notes while studying — it boosts retention.",
        "After finishing, try to explain this to someone else.",
        "Review your notes from yesterday before starting today.",
        "Try building a small example to test your understanding.",
        "Don't skip the examples — they're the best part.",
        "Practice makes permanent — apply what you learn today.",
        "Focus on understanding, not just completion.",
    ]

    while lesson_idx < len(pending):
        study_day  += 1
        day_date    = today + timedelta(days=study_day - 1)

        # insert rest day every 4 study days
        if study_day > 1 and (study_day - 1) % 4 == 0:
            rest_date = day_date
            lines.append(f"😴 **Rest Day** — {rest_date.strftime('%a, %b %d')}")
            lines.append(f"   💡 Review your notes from the past few days.")
            lines.append("")
            study_day += 1
            day_date   = today + timedelta(days=study_day - 1)

        if day_date > target:
            # ran out of days — pile remaining
            remaining = pending[lesson_idx:]
            lines.append(f"⚠️  **Remaining lessons (complete before target):**")
            for l in remaining:
                lines.append(f"   • Lesson {l.order}: {l.title} ({l.duration_min} min)")
            break

        # assign 1-2 lessons per day
        day_lessons = []
        day_mins    = 0
        while lesson_idx < len(pending) and len(day_lessons) < max_per_day and day_mins < 90:
            l = pending[lesson_idx]
            day_lessons.append(l)
            day_mins   += l.duration_min
            lesson_idx += 1

        if not day_lessons:
            break

        tip = tips[(study_day - 1) % len(tips)]
        lines.append(f"📅 **Day {study_day}** — {day_date.strftime('%a, %b %d')}")
        for l in day_lessons:
            lines.append(f"   📖 Lesson {l.order}: {l.title} ({l.duration_min} min)")
        lines.append(f"   ⏱  Total: ~{day_mins} min")
        lines.append(f"   💡 Tip: {tip}")
        lines.append("")

    lines.append("─" * 45)
    lines.append("")
    lines.append(f"✨ You've got this, {student_name}! Consistent daily effort beats cramming every time.")
    lines.append(f"📌 Complete each lesson and mark it done to track your progress.")

    return "\n".join(lines)
