from datetime import datetime
from typing import Optional, List, Union
from uuid import UUID
from pydantic import BaseModel, field_validator

class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    price: float = 0.0
    thumbnail_url: Optional[str] = None
    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v):
        if not v.strip(): raise ValueError("Title cannot be blank")
        return v.strip()
    @field_validator("price")
    @classmethod
    def price_not_negative(cls, v):
        if v < 0: raise ValueError("Price cannot be negative")
        return v

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    thumbnail_url: Optional[str] = None
    is_published: Optional[bool] = None

class CourseResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    price: float
    thumbnail_url: Optional[str] = None
    is_published: bool
    instructor_id: UUID
    created_at: datetime
    model_config = {"from_attributes": True}

class LessonCreate(BaseModel):
    title: str
    content: Optional[str] = None
    order: int
    duration_min: Optional[int] = None
    video_url: Optional[str] = None
    is_free: bool = False

class LessonUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    order: Optional[int] = None
    duration_min: Optional[int] = None
    video_url: Optional[str] = None
    is_free: Optional[bool] = None

class LessonResponse(BaseModel):
    id: UUID
    title: str
    content: Optional[str] = None
    order: int
    duration_min: Optional[int] = None
    video_url: Optional[str] = None
    is_free: bool
    course_id: UUID
    created_at: datetime
    model_config = {"from_attributes": True}

class LessonResponseLocked(BaseModel):
    id: UUID
    title: str
    order: int
    duration_min: Optional[int] = None
    is_free: bool
    is_locked: bool = True
    model_config = {"from_attributes": True}

class CourseDetailResponse(CourseResponse):
    lessons: List[Union[LessonResponse, LessonResponseLocked]] = []
    total_lessons: int = 0
    total_duration_min: int = 0

class EnrollmentResponse(BaseModel):
    id: UUID
    user_id: UUID
    course_id: UUID
    enrolled_at: datetime
    completed: bool
    completed_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

class EnrollmentWithCourse(EnrollmentResponse):
    course: CourseResponse

class ProgressUpdate(BaseModel):
    completed: bool

class ProgressResponse(BaseModel):
    id: UUID
    user_id: UUID
    lesson_id: UUID
    completed: bool
    completed_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

class CourseProgressResponse(BaseModel):
    course_id: UUID
    total_lessons: int
    completed_lessons: int
    percentage: float
    is_completed: bool

CourseDetailResponse.model_rebuild()
