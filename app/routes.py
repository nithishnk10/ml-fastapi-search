import os
import tempfile
from pathlib import Path
from fastapi import APIRouter, File, UploadFile

from app.services import search_similar_images


router = APIRouter()


@router.get("/")
def root():
    return {
        "message": "Image Similarity Search API"
    }


@router.get("/health")
def health():

    from app.services import check_health

    services = check_health()

    is_healthy = all(services.values())

    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "services": services
    }


@router.post("/search")
async def search(file: UploadFile = File(...)):

    suffix = os.path.splitext(file.filename)[1]

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp_file:

        temp_file.write(await file.read())
        temp_path = temp_file.name

    try:
        results = search_similar_images(temp_path)

        return {
            "query": file.filename,
            "matches": results
        }

    finally:
        os.remove(temp_path)


@router.post("/upload")
async def upload(file: UploadFile = File(...)):

    upload_directory = "uploads"

    os.makedirs(upload_directory, exist_ok=True)

    safe_filename = Path(file.filename).name

    file_path = os.path.join(
        upload_directory,
        safe_filename
    )

    with open(file_path, "wb") as f:
        f.write(await file.read())

    return {
        "message": "Image uploaded successfully",
        "filename": safe_filename
    }