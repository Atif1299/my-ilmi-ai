from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from .routes.quran import router as quran_router
from .routes.keywords import router as keywords_router
# from .routes.hadith import router as hadith_router
from .routes.analysis import router as analysis_router
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(quran_router, prefix="/api/quran", tags=["Quran Search"])
app.include_router(keywords_router, prefix="/api", tags=["Keywords"])
# app.include_router(hadith_router, prefix="/api/hadith", tags=["Hadith"])
app.include_router(analysis_router, prefix="/api/analysis", tags=["Analysis"])

# Mount static files (CSS, JS, images)
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend")
storage_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Storage")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")
app.mount("/storage", StaticFiles(directory=storage_path), name="storage")

# Templates for HTML rendering
templates = Jinja2Templates(directory=frontend_path)

# Frontend routes
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Serve the home page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/keywords", response_class=HTMLResponse)
async def keywords_page(request: Request):
    """Serve the keywords page"""
    return templates.TemplateResponse("keywords.html", {"request": request})

@app.get("/demo", response_class=HTMLResponse)
async def demo_page(request: Request):
    """Serve the demo page showing new interface"""
    return templates.TemplateResponse("demo.html", {"request": request})

# @app.get("/quran_search", response_class=HTMLResponse)
# async def quran_search_page(request: Request):
#     """Serve the Quran search page"""
#     return templates.TemplateResponse("quran_search.html", {"request": request})

# @app.get("/hadith_analysis", response_class=HTMLResponse)
# async def hadith_analysis_page(request: Request):
#     """Serve the Hadith analysis page"""
#     return templates.TemplateResponse("hadith_analysis.html", {"request": request})

@app.get("/analysis", response_class=HTMLResponse)
async def analysis_page(request: Request):
    """Serve the new analysis page"""
    return templates.TemplateResponse("analysis.html", {"request": request})
