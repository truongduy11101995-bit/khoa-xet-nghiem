import os
import sys
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from backend.config import FRONTEND_DIR, init_directories
from backend.database import init_db
from backend.auth import get_current_user_optional
from backend.ip_whitelist import IPWhitelistMiddleware

from backend.routers.auth import router as auth_router
from backend.routers.schedule import router as schedule_router
from backend.routers.leave import router as leave_router
from backend.routers.documents import router as document_router
from backend.routers.profiles import router as profile_router
from backend.routers.stats import router as stats_router
from backend.routers.ip_admin import router as ip_admin_router
from backend.routers.inventory import router as inventory_router
from backend.routers.environment import router as environment_router

app = FastAPI(
    title="QUẢN LÝ XÉT NGHIỆM - BV Đa khoa Thiên Ân Viễn Đông",
    description="Bệnh viện Đa khoa Thiên Ân - Viễn Đông (QĐ 2429/QĐ-BYT)",
    version="1.0.0"
)

# 1. CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. IP Whitelisting & Office Wi-Fi Protection Middleware
app.add_middleware(IPWhitelistMiddleware)

# 3. Include Routers
app.include_router(auth_router)
app.include_router(schedule_router)
app.include_router(leave_router)
app.include_router(document_router)
app.include_router(profile_router)
app.include_router(stats_router)
app.include_router(ip_admin_router)
app.include_router(inventory_router)
app.include_router(environment_router)

# 4. Mount Frontend static files
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.on_event("startup")
def on_startup():
    init_directories()
    init_db()

@app.get("/", response_class=HTMLResponse)
def index_page(request: Request):
    """Serve Dashboard or redirect to login if no token."""
    user = get_current_user_optional(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    index_html = FRONTEND_DIR / "index.html"
    if index_html.exists():
        return FileResponse(str(index_html))
    return HTMLResponse("<h1>Khoa Xét nghiệm - Bệnh viện Thiên Ân Viễn Đông</h1>")

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """Serve Login Page or redirect to dashboard if already logged in."""
    user = get_current_user_optional(request)
    if user:
        return RedirectResponse(url="/", status_code=302)

    login_html = FRONTEND_DIR / "login.html"
    if login_html.exists():
        return FileResponse(str(login_html))
    return HTMLResponse("<h1>Trang Đăng Nhập</h1>")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "system": "Khoa Xét nghiệm - BV Thiên Ân Viễn Đông",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
