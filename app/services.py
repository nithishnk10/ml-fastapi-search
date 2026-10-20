import os

import psycopg2
import torch
import open_clip
from PIL import Image
from qdrant_client import QdrantClient


# -------------------------
# Configuration
# -------------------------

MODEL_NAME = "ViT-B-32"
PRETRAINED = "laion2b_s34b_b79k"

COLLECTION_NAME = "wikiart_embeddings"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "image_similarity")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")


# -------------------------
# Load OpenCLIP
# -------------------------

model, _, preprocess = open_clip.create_model_and_transforms(
    MODEL_NAME,
    pretrained=PRETRAINED
)

model = model.to(DEVICE)
model.eval()


# -------------------------
# Database clients
# -------------------------

qdrant = QdrantClient(
    host=QDRANT_HOST,
    port=QDRANT_PORT
)


def get_postgres_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )


# -------------------------
# Generate image embedding
# -------------------------

def get_embedding(image_path):
    image = Image.open(image_path).convert("RGB")

    image_tensor = preprocess(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        embedding = model.encode_image(image_tensor)

        embedding = embedding / embedding.norm(
            dim=-1,
            keepdim=True
        )

    return embedding.cpu().numpy()[0]


# -------------------------
# Similarity search
# -------------------------

def search_similar_images(image_path, top_k=5):

    query_embedding = get_embedding(image_path)

    search_results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding.tolist(),
        limit=top_k,
    ).points

    if not search_results:
        return []

    qdrant_ids = [result.id for result in search_results]

    postgres = get_postgres_connection()

    try:
        with postgres.cursor() as cursor:

            cursor.execute(
                """
                SELECT qdrant_id, image_path, filename, artist, style
                FROM images
                WHERE qdrant_id = ANY(%s)
                """,
                (qdrant_ids,)
            )

            rows = cursor.fetchall()

    finally:
        postgres.close()

    metadata = {
        row[0]: {
            "image": row[1],
            "filename": row[2],
            "artist": row[3],
            "style": row[4],
        }
        for row in rows
    }

    results = []

    for result in search_results:

        item = metadata.get(result.id)

        if item:
            results.append({
                "image": item["image"],
                "score": float(result.score)
            })

    return results


def check_health():
    health_status = {
        "qdrant": False,
        "postgresql": False
    }

    try:
        qdrant.get_collections()
        health_status["qdrant"] = True
    except Exception:
        pass

    try:
        with get_postgres_connection() as postgres:
            with postgres.cursor() as cursor:
                cursor.execute("SELECT 1")

        health_status["postgresql"] = True

    except Exception:
        pass

    return health_status