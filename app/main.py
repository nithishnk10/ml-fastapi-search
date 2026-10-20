from fastapi import FastAPI

from app.routes import router


app = FastAPI(
    title="Image Similarity Search API",
    description="REST API for image similarity search",
    version="1.0.0"
)

app.include_router(router)