import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.routers import progress, quiz

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="AIF Study Assistant API",
    description="Adaptive quiz platform for AWS Certified AI Practitioner (AIF-C01) exam prep",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tightened to CloudFront domain via API Gateway CORS config
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(quiz.router, prefix="/api/v1")
app.include_router(progress.router, prefix="/api/v1")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# Lambda handler
handler = Mangum(app, lifespan="off")
