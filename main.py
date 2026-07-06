from fastapi import FastAPI
from api.routers import screen, confirm, report

app = FastAPI(
    title="CV Screening and Shortlisting API",
    description="An API for screening CVs based on job descriptions, scoring them, and generating a final report.",
    version="1.0.0",
)

app.include_router(screen.router, prefix="/api")
app.include_router(confirm.router, prefix="/api")
app.include_router(report.router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok"}