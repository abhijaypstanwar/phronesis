# Phronesis — φρόνησις
### AI-Powered Learning Platform

> *φρόνησις (phronesis) — Greek for practical wisdom: the ability to make the right decision in a given situation.*

Phronesis is a full-stack, AI-powered learning platform built as an 8-week software engineering internship project at **Diebold Nixdorf**, under the guidance of Ms. Maheshwari Swati, Mr. Sankalp Singhal, and Mr. Rafal Chodzidlo.

Built solo. From scratch. In 8 weeks.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [AI Features](#ai-features)
- [Security](#security)
- [Docker Deployment](#docker-deployment)
- [Getting Started](#getting-started)

---

## Features

### Student
- Register, verify email via OTP, and log in securely
- Browse and enroll in courses
- Read lessons and mark them complete — progress tracked in real time
- Chat with an AI tutor grounded in actual course lesson content
- Generate a personalised day-by-day study plan from remaining lessons and a target date
- Take topic-specific quizzes with instant scoring and explanations
- Access a general AI assistant on the dashboard aware of all enrolled courses

### Administrator
- View live platform statistics (users, enrollments, lessons completed)
- Search, deactivate, reactivate, and delete user accounts

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python · FastAPI · Uvicorn |
| ORM | SQLAlchemy |
| Database | SQLite (dev) · PostgreSQL-ready |
| Validation | Pydantic v2 |
| Authentication | JWT (HS256) via python-jose |
| Password Security | bcrypt via passlib |
| Email | Gmail SMTP (port 465, SSL) |
| AI / LLM | Ollama · llama3.2 (local) |
| Frontend | Vanilla HTML · CSS · JavaScript |
| Deployment | Docker · Docker Compose |

---

## Project Structure

```
FirstProject/
├── app/
│   ├── config.py               # Environment variable loading
│   ├── database.py             # SQLAlchemy engine, session, Base
│   ├── main.py                 # FastAPI app factory, routers, page routes
│   ├── models/
│   │   ├── user.py             # User model — 17 columns
│   │   ├── course.py           # Course model
│   │   ├── lesson.py           # Lesson model
│   │   ├── enrollment.py       # Enrollment junction table
│   │   ├── progress.py         # Progress junction table
│   │   ├── study_plan.py       # Study plan model
│   │   └── quiz.py             # Quiz result model
│   ├── schemas/
│   │   ├── user.py             # User request/response schemas
│   │   └── course.py           # Course/lesson schemas
│   ├── routers/
│   │   ├── auth.py             # 8 authentication endpoints
│   │   ├── admin.py            # 6 administration endpoints
│   │   └── courses.py          # 15+ course, quiz, chat, study plan endpoints
│   └── services/
│       ├── auth.py             # JWT, bcrypt, get_current_user()
│       ├── email.py            # OTP generation, Gmail SMTP
│       ├── study_plan.py       # Deterministic scheduling algorithm
│       ├── quiz_generator.py   # Topic-specific MCQ question banks
│       └── ollama_chat.py      # Ollama client, course and dashboard chat
├── static/
│   ├── style.css               # Shared CSS design system
│   └── app.js                  # Shared JavaScript utilities
├── welcome.html                # Landing page
├── index.html                  # Login / Register
├── verify.html                 # OTP verification
├── forgot.html                 # Forgot password
├── reset.html                  # Password reset
├── dashboard.html              # Student dashboard + AI assistant
├── courses.html                # Course browser
├── course_detail.html          # Lessons, quiz, study plan, AI tutor
├── admin.html                  # Admin panel
├── profile.html                # User profile
├── main.py                     # Entry point
├── seed.py                     # Seeds sample courses into the database
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env
```

---

## Database Schema

### `users`
| Column | Type | Description |
|---|---|---|
| id | String (UUID) | Primary key — UUID prevents sequential enumeration |
| email | String | Unique, indexed |
| password | String | bcrypt hash — plaintext never stored |
| name | String | Display name |
| role | String | `student` or `admin` |
| is_active | Boolean | Deactivated accounts cannot log in |
| is_verified | Boolean | Set to True after OTP verification |
| otp_code | String | 6-digit one-time password |
| otp_expires_at | DateTime (UTC) | OTP valid for 10 minutes |
| reset_token | String | Cryptographically random reset token |
| reset_token_expires_at | DateTime (UTC) | Token valid for 15 minutes, single-use |
| last_login | DateTime (UTC) | Updated on every successful login |
| phone | String | Optional |
| dob | String | Date of birth, optional |
| address | String | Optional |
| created_at | DateTime (UTC) | Auto-set on creation |
| updated_at | DateTime (UTC) | Auto-updated on save |

---

### `courses`
| Column | Type | Description |
|---|---|---|
| id | String (UUID) | Primary key |
| title | String | Course title |
| description | Text | Course description |
| price | Float | 0.0 = free |
| thumbnail_url | String | Optional |
| is_published | Boolean | Only published courses visible to students |
| instructor_id | String (FK) | Foreign key → users.id |
| created_at | DateTime (UTC) | — |
| updated_at | DateTime (UTC) | — |

---

### `lessons`
| Column | Type | Description |
|---|---|---|
| id | String (UUID) | Primary key |
| course_id | String (FK) | Foreign key → courses.id (cascade delete) |
| title | String | Lesson title |
| content | Text | Full written lesson content |
| order | Integer | Sort position within the course |
| duration_min | Integer | Estimated reading time in minutes |
| video_url | String | Optional |
| is_free | Boolean | Free preview — accessible without enrollment |
| created_at | DateTime (UTC) | — |
| updated_at | DateTime (UTC) | — |

---

### `enrollments`
| Column | Type | Description |
|---|---|---|
| id | String (UUID) | Primary key |
| user_id | String (FK) | Foreign key → users.id |
| course_id | String (FK) | Foreign key → courses.id |
| enrolled_at | DateTime (UTC) | Enrollment timestamp |
| completed | Boolean | True when all lessons marked complete |
| completed_at | DateTime (UTC) | Set when course is completed |

---

### `progress`
| Column | Type | Description |
|---|---|---|
| id | String (UUID) | Primary key |
| user_id | String (FK) | Foreign key → users.id |
| lesson_id | String (FK) | Foreign key → lessons.id |
| completed | Boolean | Whether the lesson is marked complete |
| completed_at | DateTime (UTC) | Timestamp of completion |

---

### `study_plans`
| Column | Type | Description |
|---|---|---|
| id | String (UUID) | Primary key |
| user_id | String | User who owns the plan |
| course_id | String | Course the plan is for |
| plan_text | Text | Full formatted day-by-day schedule |
| target_date | String | The student's chosen completion date |
| created_at | DateTime (UTC) | — |
| updated_at | DateTime (UTC) | Overwritten on regeneration |

---

### `quiz_results`
| Column | Type | Description |
|---|---|---|
| id | String (UUID) | Primary key |
| user_id | String | Student who took the quiz |
| course_id | String | Course the quiz belongs to |
| lesson_id | String | Lesson the quiz is for |
| score | Integer | Number of correct answers |
| total | Integer | Total number of questions |
| questions | Text | JSON string of questions asked |
| answers | Text | JSON string of student's answers |
| taken_at | DateTime (UTC) | Timestamp of attempt |

---

## API Endpoints

### Authentication — `/api/auth`
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/register` | Public | Register, hash password, send OTP, return JWT |
| POST | `/login` | Public | Verify credentials, return JWT |
| GET | `/me` | Bearer | Return current user |
| POST | `/verify-otp` | Public | Validate OTP, activate account |
| POST | `/resend-otp` | Public | Resend verification OTP |
| POST | `/forgot-password` | Public | Send reset email (anti-enumeration protected) |
| POST | `/reset-password` | Public | Reset password, invalidate token |
| PATCH | `/profile` | Bearer | Update profile or change password |

### Administration — `/api/admin`
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/setup` | Public | Create first admin (one-time) |
| GET | `/stats` | Admin | Live platform statistics |
| GET | `/users` | Admin | All users |
| GET | `/users/active` | Admin | Users active in last 24h |
| PATCH | `/users/{id}/deactivate` | Admin | Deactivate account |
| PATCH | `/users/{id}/reactivate` | Admin | Reactivate account |
| DELETE | `/users/{id}` | Admin | Delete account (cascade) |

### Courses — `/api/courses`
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/` | Bearer | List published courses |
| POST | `/` | Admin | Create course |
| GET | `/my` | Bearer | Enrolled courses |
| POST | `/dashboard/chat` | Bearer | Dashboard AI assistant |
| GET | `/{id}` | Bearer | Course detail with lessons |
| PATCH | `/{id}` | Admin | Update course |
| DELETE | `/{id}` | Admin | Delete course |
| POST | `/{id}/lessons` | Admin | Add lesson |
| PATCH | `/{id}/lessons/{lid}` | Admin | Update lesson |
| DELETE | `/{id}/lessons/{lid}` | Admin | Delete lesson |
| POST | `/{id}/enroll` | Bearer | Enroll |
| DELETE | `/{id}/enroll` | Bearer | Unenroll |
| POST | `/{id}/lessons/{lid}/progress` | Bearer | Mark complete/incomplete |
| GET | `/{id}/progress` | Bearer | Get progress |
| POST | `/{id}/study-plan` | Bearer | Generate study plan |
| GET | `/{id}/study-plan` | Bearer | Get saved study plan |
| GET | `/{id}/lessons/{lid}/quiz` | Bearer | Get quiz questions |
| POST | `/{id}/lessons/{lid}/quiz/submit` | Bearer | Submit answers |
| GET | `/{id}/quiz-results` | Bearer | Past quiz scores |
| POST | `/{id}/chat` | Bearer | Course AI tutor |

---

## AI Features

### Course Tutor
Powered by **Ollama** running **llama3.2** locally. When a student asks a question, the system fetches all lesson content from the database and provides it to the model as context. The model is instructed to answer only from that material.

- **Enrolled students** → deep, content-specific answers
- **Non-enrolled visitors** → brief overview only
- **Chat history** persisted in browser localStorage, keyed by course ID

### Study Plan Generator
A deterministic scheduling algorithm — no external API.

- Filters pending (incomplete) lessons
- Distributes across available days: max 2 lessons/day, max 90 min/day
- Inserts a rest day every 4 consecutive study days
- Handles edge cases: past target dates, all lessons already complete
- Plan saved to database, retrievable at any time

### Quiz Engine
Handcrafted topic-specific MCQ banks — no auto-generation.

Topics covered: Python introduction, variables and data types, loops, functions, FastAPI and REST APIs, SQLAlchemy and ORM, JWT and authentication, AI and machine learning, Docker.

- 5 questions per lesson
- Instant scoring with colour-coded feedback
- Explanation shown for every answer
- Results persisted to `quiz_results` table

---

## Security

| Feature | Implementation |
|---|---|
| Password hashing | bcrypt (work factor 12) via passlib |
| Authentication | JWT HS256, 24-hour expiry |
| OTP | 6-digit, 10-minute expiry, cleared after use |
| Reset token | `secrets.token_urlsafe(32)`, 15-minute expiry, single-use |
| Anti-enumeration | Forgot-password always returns HTTP 200 regardless of email existence |
| Role-based access | `require_admin()` dependency on all admin routes |
| Secrets | `.env` file, listed in `.gitignore` |

---

## Docker Deployment

```bash
# 1. Make sure Ollama is running
# Open http://localhost:11434 — should say "Ollama is running"

# 2. Build the image
docker compose build

# 3. Start the container
docker compose up

# 4. Create admin (one-time, via browser)
# Open http://localhost:8000/docs → POST /api/admin/setup

# 5. Seed sample courses (run inside the container)
docker compose exec api python seed.py

# 6. Open the app
# http://localhost:8000
```

> **Note:** Ollama runs on the host machine. Inside Docker, `localhost` refers to the container. The Ollama client is configured with `host='http://host.docker.internal:11434'` to bridge this gap.

---

## Getting Started (without Docker)

```bash
# Clone the repo
git clone https://github.com/abhijaypstanwar/Project-1
cd Project-1

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Fill in your values

# Run the app
python main.py

# Seed sample courses
python seed.py

# Open http://localhost:8000
```

> **Python version:** 3.11+ recommended. bcrypt must be pinned to `4.0.1`.

---

## Key Engineering Decisions

**Rule-based study plan over AI API** — The Gemini API was initially integrated but produced inconsistent outputs. A deterministic algorithm was built instead, which is more reliable, costs nothing, and has no external dependencies.

**Handcrafted quiz questions over auto-generation** — Pattern-based extraction from lesson text produced unreliable and sometimes nonsensical questions. Handcrafted, topic-specific question banks were written instead.

**Local LLM over cloud API** — Ollama runs entirely on the local machine. No course content is transmitted to any external server. No API costs. No quota limits.

> *The best tool is not always the correct solution.*

---

## Seeded Sample Courses

| Course | Price | Lessons |
|---|---|---|
| Python for Beginners | Free | 5 |
| Web Development with FastAPI | ₹999 | 6 |
| Introduction to AI & ML | ₹1499 | 5 |

---

*Built by Abhijay Pratap Singh Tanwar — 8-week internship at Diebold Nixdorf, 2026*
