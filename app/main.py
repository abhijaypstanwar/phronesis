import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import create_tables
from app.routers import auth as auth_router
from app.routers import admin as admin_router
from app.routers import courses as courses_router

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, version="1.0.0")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

    @app.on_event("startup")
    def on_startup():
        import app.models
        create_tables()

    app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

    pages = {
        "/": "welcome.html", "/welcome": "welcome.html", "/login": "index.html",
        "/verify": "verify.html", "/forgot": "forgot.html", "/reset": "reset.html",
        "/dashboard": "dashboard.html", "/courses": "courses.html",
        "/admin": "admin.html", "/profile": "profile.html",
    }
    for path, filename in pages.items():
        file_path = os.path.join(BASE_DIR, filename)
        app.add_api_route(path, lambda fp=file_path: FileResponse(fp), methods=["GET"])

    @app.get("/course/{course_id}")
    def serve_course_detail(course_id: str):
        return FileResponse(os.path.join(BASE_DIR, "course_detail.html"))

    app.include_router(auth_router.router)
    app.include_router(admin_router.router)
    app.include_router(courses_router.router)

    @app.get("/health")
    def health():
        return {"status": "ok", "app": settings.APP_NAME}

    return app

app = create_app()
