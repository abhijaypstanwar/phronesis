"""
app/services/study_plan_generator.py

Rule-based study plan generator. Fully replaces the Gemini-based generator
for the Week 6 feature — no external API calls, no quota limits.

Given a list of lessons, which lesson ids are already completed, and a
target completion date, this back-calculates a day-by-day plan:
  - Distributes pending lessons evenly across available study days
  - Inserts a rest day roughly every 3-4 study days
  - Flags the plan as "ambitious" if the pace is heavy (>3 lessons/day)
  - Finishes early if lessons run out before the target date (no filler days)

This module has no ORM/FastAPI dependencies — it operates on plain dicts —
so it's easy to unit test and easy to swap out later if needed.
"""

import math
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


DEFAULT_LESSON_MINUTES = 30
REST_DAY_INTERVAL = 4  # insert a rest day after every 3-4 study days


@dataclass
class LessonBrief:
    id: str
    title: str
    order: int
    duration_minutes: int = DEFAULT_LESSON_MINUTES


@dataclass
class StudyPlanDay:
    day_number: int
    date: date
    is_rest_day: bool
    lessons: list = field(default_factory=list)  # list[LessonBrief] as dicts
    estimated_minutes: int = 0


@dataclass
class StudyPlanResult:
    target_date: date
    total_days: int
    pending_lesson_count: int
    is_ambitious: bool
    message: Optional[str]
    days: list  # list[StudyPlanDay]


class StudyPlanGenerationError(ValueError):
    """Raised when a plan can't be generated (e.g. target date not in the future)."""


def generate_rule_based_study_plan(
    lessons: list[LessonBrief],
    completed_lesson_ids: set,
    target_date: date,
    start_date: Optional[date] = None,
) -> StudyPlanResult:
    start_date = start_date or date.today()

    if target_date <= start_date:
        raise StudyPlanGenerationError("Target completion date must be after today.")

    pending = sorted(
        [l for l in lessons if l.id not in completed_lesson_ids],
        key=lambda l: l.order,
    )

    total_days = (target_date - start_date).days  # number of days from tomorrow through target_date

    if not pending:
        return StudyPlanResult(
            target_date=target_date,
            total_days=total_days,
            pending_lesson_count=0,
            is_ambitious=False,
            message="All lessons in this course are already completed — no plan needed.",
            days=[],
        )

    # Work out how many of the available days should be study days vs rest days.
    max_rest_days = total_days // REST_DAY_INTERVAL
    study_days_count = total_days - max_rest_days
    if study_days_count < 1:
        # Target date is too tight to fit any rest days — study every day.
        study_days_count = total_days
        max_rest_days = 0

    lessons_per_day = math.ceil(len(pending) / study_days_count)
    is_ambitious = lessons_per_day > 3

    message = None
    if is_ambitious:
        message = (
            f"This timeline needs about {lessons_per_day} lessons/day to finish "
            f"by {target_date.isoformat()}. Consider pushing the target date out "
            f"for a more comfortable pace."
        )

    days: list[StudyPlanDay] = []
    lesson_idx = 0
    study_day_streak = 0
    current_date = start_date

    for day_number in range(1, total_days + 1):
        current_date += timedelta(days=1)
        remaining_lessons = len(pending) - lesson_idx
        remaining_days = total_days - day_number + 1

        # Decide if this should be a rest day: every REST_DAY_INTERVAL-th day,
        # but never rest if we're out of slack (remaining_days == remaining
        # study days needed) and never rest after all lessons are assigned.
        would_rest = max_rest_days > 0 and study_day_streak >= (REST_DAY_INTERVAL - 1)
        must_study = remaining_lessons > 0 and remaining_days <= _days_needed(remaining_lessons, lessons_per_day)

        if would_rest and not must_study and remaining_lessons > 0:
            days.append(StudyPlanDay(day_number=day_number, date=current_date, is_rest_day=True))
            study_day_streak = 0
            max_rest_days -= 1
            continue

        if remaining_lessons == 0:
            # Nothing left to schedule — stop the plan early rather than padding it out.
            break

        chunk = pending[lesson_idx: lesson_idx + lessons_per_day]
        lesson_idx += len(chunk)
        study_day_streak += 1

        days.append(
            StudyPlanDay(
                day_number=day_number,
                date=current_date,
                is_rest_day=False,
                lessons=[
                    {"id": l.id, "title": l.title, "order": l.order, "duration_minutes": l.duration_minutes}
                    for l in chunk
                ],
                estimated_minutes=sum(l.duration_minutes for l in chunk),
            )
        )

    return StudyPlanResult(
        target_date=target_date,
        total_days=total_days,
        pending_lesson_count=len(pending),
        is_ambitious=is_ambitious,
        message=message,
        days=days,
    )


def _days_needed(remaining_lessons: int, lessons_per_day: int) -> int:
    return math.ceil(remaining_lessons / lessons_per_day)