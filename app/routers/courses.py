from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.lesson import Lesson
from app.models.progress import Progress
from app.models.study_plan import StudyPlan
from app.models.user import User
from app.schemas.course import (
    CourseCreate, CourseDetailResponse, CourseProgressResponse,
    CourseResponse, CourseUpdate, EnrollmentResponse, EnrollmentWithCourse,
    LessonCreate, LessonResponse, LessonResponseLocked, LessonUpdate,
    ProgressResponse, ProgressUpdate,
)
from app.services.auth import get_current_user, require_admin
from app.services.study_plan import generate_study_plan, LessonInfo

router = APIRouter(prefix="/api/courses", tags=["Courses"])

# ── helpers ──
def is_enrolled(db, user_id, course_id):
    return db.query(Enrollment).filter(Enrollment.user_id == user_id, Enrollment.course_id == course_id).first() is not None

def is_instructor_or_admin(user, course):
    return user.role == "admin" or str(user.id) == str(course.instructor_id)

# ── COURSES ──
@router.get("/", response_model=List[CourseResponse])
def list_courses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "admin":
        courses = db.query(Course).order_by(Course.created_at.desc()).all()
    else:
        courses = db.query(Course).filter(Course.is_published == True).order_by(Course.created_at.desc()).all()
    return [CourseResponse.model_validate(c) for c in courses]

@router.post("/", response_model=CourseResponse, status_code=201)
def create_course(payload: CourseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ("admin", "instructor"):
        raise HTTPException(status_code=403, detail="Only admins and instructors can create courses")
    course = Course(title=payload.title, description=payload.description, price=payload.price,
                    thumbnail_url=payload.thumbnail_url, instructor_id=str(current_user.id))
    db.add(course); db.commit(); db.refresh(course)
    return CourseResponse.model_validate(course)

@router.get("/my", response_model=List[EnrollmentWithCourse])
def my_courses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    enrollments = db.query(Enrollment).filter(Enrollment.user_id == str(current_user.id)).all()
    result = []
    for e in enrollments:
        course = db.query(Course).filter(Course.id == e.course_id).first()
        if course:
            result.append(EnrollmentWithCourse(
                **EnrollmentResponse.model_validate(e).model_dump(),
                course=CourseResponse.model_validate(course),
            ))
    return result

@router.get("/{course_id}", response_model=CourseDetailResponse)
def get_course(course_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course: raise HTTPException(status_code=404, detail="Course not found")
    if not course.is_published and not is_instructor_or_admin(current_user, course):
        raise HTTPException(status_code=404, detail="Course not found")
    enrolled = is_enrolled(db, str(current_user.id), course_id)
    lessons  = db.query(Lesson).filter(Lesson.course_id == course_id).order_by(Lesson.order).all()
    lesson_responses = []
    for l in lessons:
        if enrolled or is_instructor_or_admin(current_user, course) or l.is_free:
            lesson_responses.append(LessonResponse.model_validate(l))
        else:
            lesson_responses.append(LessonResponseLocked(id=l.id, title=l.title, order=l.order, duration_min=l.duration_min, is_free=l.is_free, is_locked=True))
    return CourseDetailResponse(
        **CourseResponse.model_validate(course).model_dump(),
        lessons=lesson_responses,
        total_lessons=len(lessons),
        total_duration_min=sum(l.duration_min or 0 for l in lessons),
    )

@router.patch("/{course_id}", response_model=CourseResponse)
def update_course(course_id: str, payload: CourseUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course: raise HTTPException(status_code=404, detail="Course not found")
    if not is_instructor_or_admin(current_user, course): raise HTTPException(status_code=403, detail="Not authorised")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(course, field, value)
    db.commit(); db.refresh(course)
    return CourseResponse.model_validate(course)

@router.delete("/{course_id}", status_code=204)
def delete_course(course_id: str, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course: raise HTTPException(status_code=404, detail="Course not found")
    db.delete(course); db.commit()

# ── LESSONS ──
@router.post("/{course_id}/lessons", response_model=LessonResponse, status_code=201)
def create_lesson(course_id: str, payload: LessonCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course: raise HTTPException(status_code=404, detail="Course not found")
    if not is_instructor_or_admin(current_user, course): raise HTTPException(status_code=403, detail="Not authorised")
    lesson = Lesson(title=payload.title, content=payload.content, order=payload.order,
                    duration_min=payload.duration_min, video_url=payload.video_url,
                    is_free=payload.is_free, course_id=course_id)
    db.add(lesson); db.commit(); db.refresh(lesson)
    return LessonResponse.model_validate(lesson)

@router.patch("/{course_id}/lessons/{lesson_id}", response_model=LessonResponse)
def update_lesson(course_id: str, lesson_id: str, payload: LessonUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course: raise HTTPException(status_code=404, detail="Course not found")
    if not is_instructor_or_admin(current_user, course): raise HTTPException(status_code=403, detail="Not authorised")
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id, Lesson.course_id == course_id).first()
    if not lesson: raise HTTPException(status_code=404, detail="Lesson not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(lesson, field, value)
    db.commit(); db.refresh(lesson)
    return LessonResponse.model_validate(lesson)

@router.delete("/{course_id}/lessons/{lesson_id}", status_code=204)
def delete_lesson(course_id: str, lesson_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course: raise HTTPException(status_code=404, detail="Course not found")
    if not is_instructor_or_admin(current_user, course): raise HTTPException(status_code=403, detail="Not authorised")
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id, Lesson.course_id == course_id).first()
    if not lesson: raise HTTPException(status_code=404, detail="Lesson not found")
    db.delete(lesson); db.commit()

# ── ENROLLMENTS ──
@router.post("/{course_id}/enroll", response_model=EnrollmentResponse, status_code=201)
def enroll(course_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    course = db.query(Course).filter(Course.id == course_id, Course.is_published == True).first()
    if not course: raise HTTPException(status_code=404, detail="Course not found")
    if is_enrolled(db, str(current_user.id), course_id):
        raise HTTPException(status_code=409, detail="Already enrolled")
    enrollment = Enrollment(user_id=str(current_user.id), course_id=course_id)
    db.add(enrollment); db.commit(); db.refresh(enrollment)
    return EnrollmentResponse.model_validate(enrollment)

@router.delete("/{course_id}/enroll", status_code=204)
def unenroll(course_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    enrollment = db.query(Enrollment).filter(Enrollment.user_id == str(current_user.id), Enrollment.course_id == course_id).first()
    if not enrollment: raise HTTPException(status_code=404, detail="Not enrolled")
    db.delete(enrollment); db.commit()

# ── PROGRESS ──
@router.post("/{course_id}/lessons/{lesson_id}/progress", response_model=ProgressResponse)
def update_progress(course_id: str, lesson_id: str, payload: ProgressUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not is_enrolled(db, str(current_user.id), course_id):
        raise HTTPException(status_code=403, detail="Must be enrolled to track progress")
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id, Lesson.course_id == course_id).first()
    if not lesson: raise HTTPException(status_code=404, detail="Lesson not found")
    prog = db.query(Progress).filter(Progress.user_id == str(current_user.id), Progress.lesson_id == lesson_id).first()
    if prog:
        prog.completed = payload.completed
        prog.completed_at = datetime.now(timezone.utc) if payload.completed else None
    else:
        prog = Progress(user_id=str(current_user.id), lesson_id=lesson_id,
                        completed=payload.completed, completed_at=datetime.now(timezone.utc) if payload.completed else None)
        db.add(prog)
    db.commit(); db.refresh(prog)
    all_lessons = db.query(Lesson).filter(Lesson.course_id == course_id).all()
    done_count  = db.query(Progress).filter(Progress.user_id == str(current_user.id),
                    Progress.lesson_id.in_([l.id for l in all_lessons]), Progress.completed == True).count()
    if done_count == len(all_lessons):
        enr = db.query(Enrollment).filter(Enrollment.user_id == str(current_user.id), Enrollment.course_id == course_id).first()
        if enr and not enr.completed:
            enr.completed = True; enr.completed_at = datetime.now(timezone.utc); db.commit()
    return ProgressResponse.model_validate(prog)

@router.get("/{course_id}/progress", response_model=CourseProgressResponse)
def get_progress(course_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not is_enrolled(db, str(current_user.id), course_id):
        raise HTTPException(status_code=403, detail="Must be enrolled to view progress")
    all_lessons = db.query(Lesson).filter(Lesson.course_id == course_id).all()
    total = len(all_lessons)
    if total == 0:
        return CourseProgressResponse(course_id=course_id, total_lessons=0, completed_lessons=0, percentage=0.0, is_completed=False)
    completed = db.query(Progress).filter(Progress.user_id == str(current_user.id),
                    Progress.lesson_id.in_([l.id for l in all_lessons]), Progress.completed == True).count()
    enr = db.query(Enrollment).filter(Enrollment.user_id == str(current_user.id), Enrollment.course_id == course_id).first()
    return CourseProgressResponse(course_id=course_id, total_lessons=total, completed_lessons=completed,
                                  percentage=round((completed / total) * 100, 1), is_completed=enr.completed if enr else False)

# ── STUDY PLAN ──
@router.post("/{course_id}/study-plan")
def create_study_plan(course_id: str, target_date: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not is_enrolled(db, str(current_user.id), course_id):
        raise HTTPException(status_code=403, detail="Must be enrolled to generate a study plan")
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course: raise HTTPException(status_code=404, detail="Course not found")
    lessons = db.query(Lesson).filter(Lesson.course_id == course_id).order_by(Lesson.order).all()
    completed_ids = [p.lesson_id for p in db.query(Progress).filter(
        Progress.user_id == str(current_user.id), Progress.completed == True).all()]
    lesson_infos = [LessonInfo(id=l.id, order=l.order, title=l.title, duration_min=l.duration_min or 20) for l in lessons]
    plan_text = generate_study_plan(
        course_title=course.title, lessons=lesson_infos,
        completed_ids=completed_ids, target_date=target_date, student_name=current_user.name,
    )
    existing = db.query(StudyPlan).filter(StudyPlan.user_id == str(current_user.id), StudyPlan.course_id == course_id).first()
    if existing:
        existing.plan_text = plan_text; existing.target_date = target_date; db.commit(); db.refresh(existing)
    else:
        sp = StudyPlan(user_id=str(current_user.id), course_id=course_id, plan_text=plan_text, target_date=target_date)
        db.add(sp); db.commit()
    return {"course_id": course_id, "target_date": target_date, "plan": plan_text}

@router.get("/{course_id}/study-plan")
def get_study_plan(course_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = db.query(StudyPlan).filter(StudyPlan.user_id == str(current_user.id), StudyPlan.course_id == course_id).first()
    if not plan: raise HTTPException(status_code=404, detail="No study plan found")
    return {"course_id": course_id, "target_date": plan.target_date, "plan": plan.plan_text}
