from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Image Similarity Search API"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert "status" in data
    assert "services" in data
    assert "qdrant" in data["services"]
    assert "postgresql" in data["services"]


def test_search():
    image = Image.new("RGB", (224, 224), "white")

    image_bytes = BytesIO()
    image.save(image_bytes, format="JPEG")
    image_bytes.seek(0)

    response = client.post(
        "/search",
        files={
            "file": (
                "test.jpg",
                image_bytes,
                "image/jpeg"
            )
        }
    )

    assert response.status_code == 200
    assert response.json()["query"] == "test.jpg"
    assert "matches" in response.json()