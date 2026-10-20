# Image Similarity Search API

A FastAPI backend that exposes image similarity search through REST APIs.

The API uses the image embeddings generated in the previous image similarity search task.

## Architecture

```text
Client
   |
   v
FastAPI
   |
   v
OpenCLIP
   |
   v
Qdrant ----> PostgreSQL
   |
   v
Similarity Results
```

## Features

- Image similarity search using OpenCLIP
- Vector similarity search using Qdrant
- Image metadata stored in PostgreSQL
- REST APIs using FastAPI
- Image upload endpoint
- Health check for Qdrant and PostgreSQL
- Swagger API documentation
- Automated API tests
- Docker support

## API Endpoints

### GET /

Returns basic API information.

### GET /health

Checks the health of the API dependencies.

Example response:

```json
{
  "status": "healthy",
  "services": {
    "qdrant": true,
    "postgresql": true
  }
}
```

### POST /search

Accepts an image and returns the top 5 visually similar images.

Request:

```text
multipart/form-data
file: image.jpg
```

Example response:

```json
{
  "query": "image.jpg",
  "matches": [
    {
      "image": "dataset_10k/Northern_Renaissance/example.jpg",
      "score": 0.94
    }
  ]
}
```

### POST /upload

Uploads and stores an image in the `uploads/` directory.

Example response:

```json
{
  "message": "Image uploaded successfully",
  "filename": "image.jpg"
}
```

## Project Structure

```text
ml-fastapi-search/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   └── services.py
├── tests/
│   └── test_api.py
├── .gitignore
├── Dockerfile
├── pytest.ini
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.12
- Docker
- Qdrant
- PostgreSQL

The Qdrant and PostgreSQL instances contain the embeddings and metadata generated in the previous task.

## Local Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install PyTorch CPU:

```powershell
pip install torch==2.14.1+cpu torchvision==0.29.1+cpu --index-url https://download.pytorch.org/whl/cpu
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Start the API:

```powershell
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Database Configuration

The application uses environment variables for Qdrant and PostgreSQL.

### Qdrant

```text
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### PostgreSQL

```text
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=image_similarity
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

## Running Tests

Run:

```powershell
pytest
```

The test suite verifies the API routes and response structures.

## Docker

Build the image:

```powershell
docker build -t ml-fastapi-search .
```

Run the container:

```powershell
docker run --rm -p 8000:8000 `
  --add-host=host.docker.internal:host-gateway `
  -e QDRANT_HOST=host.docker.internal `
  -e QDRANT_PORT=6333 `
  -e POSTGRES_HOST=host.docker.internal `
  -e POSTGRES_PORT=5432 `
  -e POSTGRES_DB=image_similarity `
  -e POSTGRES_USER=postgres `
  -e POSTGRES_PASSWORD=postgres `
  ml-fastapi-search
```

The API will then be available at:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Technologies

- Python
- FastAPI
- OpenCLIP
- Qdrant
- PostgreSQL
- PyTorch
- Docker
- Pytest
