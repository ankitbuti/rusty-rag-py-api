# Deployment Guide for Google Cloud Run

This guide explains how to deploy the Rusty-RAG API to Google Cloud Run using Gunicorn.

## Prerequisites

1. Google Cloud SDK installed and configured
2. Docker installed
3. A Google Cloud project with Cloud Run API enabled

## Environment Variables

Set the following environment variables in Google Cloud Run:

- `WEAVIATE_URL`: Your Weaviate cluster URL
- `WEAVIATE_API_KEY`: Your Weaviate API key
- `PORT`: Port number (default: 8080, automatically set by Cloud Run)

## Deployment Steps

### 1. Build and Deploy with gcloud

```bash
# Build and deploy to Cloud Run
gcloud run deploy rusty-rag-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars WEAVIATE_URL=your_weaviate_url,WEAVIATE_API_KEY=your_api_key
```

### 2. Build and Deploy with Docker

```bash
# Build the Docker image
docker build -t gcr.io/your-project/rusty-rag-api .

# Push to Google Container Registry
docker push gcr.io/your-project/rusty-rag-api

# Deploy to Cloud Run
gcloud run deploy rusty-rag-api \
  --image gcr.io/your-project/rusty-rag-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars WEAVIATE_URL=your_weaviate_url,WEAVIATE_API_KEY=your_api_key
```

## Configuration Details

### Gunicorn Configuration

The application uses Gunicorn with the following optimized settings for Cloud Run:

- **Workers**: 1 (recommended for Cloud Run)
- **Worker Class**: `uvicorn.workers.UvicornWorker` (for async FastAPI support)
- **Timeout**: 120 seconds
- **Keep-alive**: 2 seconds
- **Max requests**: 1000 (with jitter for graceful restarts)

### Docker Configuration

- **Base Image**: Python 3.11 slim
- **Port**: 8080 (configurable via PORT environment variable)
- **Health Check**: Built-in health check endpoint at `/health`
- **Security**: Non-root user execution

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /hello/{name}` - Personalized greeting
- `POST /records` - Create a single record
- `POST /records/batch` - Create multiple records
- `POST /search` - Search records
- `GET /records` - Get all records (paginated)
- `GET /records/{record_id}` - Get specific record

## Monitoring

The application includes:
- Health check endpoint for monitoring
- Structured logging
- Error handling with appropriate HTTP status codes

## Local Development

For local development, you can still run the application directly:

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py
```

The application will start on `http://localhost:8080` by default.

## Troubleshooting

### Common Issues

1. **Weaviate Connection Errors**: Ensure `WEAVIATE_URL` and `WEAVIATE_API_KEY` are set correctly
2. **Port Issues**: Cloud Run automatically sets the PORT environment variable
3. **Memory Issues**: Adjust Cloud Run memory allocation if needed
4. **Timeout Issues**: The Gunicorn timeout is set to 120 seconds

### Logs

View logs in Google Cloud Console:
```bash
gcloud logs read --service=rusty-rag-api --limit=50
```
