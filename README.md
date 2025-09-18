# Hello World FastAPI on Google Cloud Run

A simple FastAPI application with a hello world endpoint, ready for deployment on Google Cloud Run.

## Features

- FastAPI application with multiple endpoints
- Docker containerization
- Google Cloud Run deployment configuration
- Health check endpoint
- CORS middleware enabled

## API Endpoints

- `GET /` - Root endpoint with hello world message
- `GET /health` - Health check endpoint for monitoring
- `GET /hello/{name}` - Personalized hello endpoint

## Local Development

### Prerequisites

- Python 3.11+
- pip

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application locally:
```bash
python main.py
```

The API will be available at `http://localhost:8080`

### Using Docker locally

1. Build the Docker image:
```bash
docker build -t hello-world-api .
```

2. Run the container:
```bash
docker run -p 8080:8080 hello-world-api
```

## Google Cloud Run Deployment

### Prerequisites

- Google Cloud SDK installed and configured
- Docker installed
- A Google Cloud project with the following APIs enabled:
  - Cloud Run API
  - Cloud Build API
  - Container Registry API

### Method 1: Using Cloud Build (Recommended)

1. Connect your repository to Google Cloud Build or push your code to a Git repository.

2. Create a Cloud Build trigger:
```bash
gcloud builds triggers create github \
  --repo-name=your-repo-name \
  --repo-owner=your-github-username \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml
```

3. Push your code to trigger the build and deployment.

### Method 2: Manual Deployment

1. Build and push the Docker image:
```bash
# Set your project ID
export PROJECT_ID=your-project-id

# Build the image
docker build -t gcr.io/$PROJECT_ID/hello-world-api .

# Push the image
docker push gcr.io/$PROJECT_ID/hello-world-api
```

2. Deploy to Cloud Run:
```bash
gcloud run deploy hello-world-api \
  --image gcr.io/$PROJECT_ID/hello-world-api \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10
```

### Method 3: Direct Deployment from Source

```bash
gcloud run deploy hello-world-api \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080
```

## Testing the Deployment

Once deployed, you can test the endpoints:

```bash
# Get the service URL
SERVICE_URL=$(gcloud run services describe hello-world-api --region=us-central1 --format='value(status.url)')

# Test the root endpoint
curl $SERVICE_URL/

# Test the health endpoint
curl $SERVICE_URL/health

# Test the personalized endpoint
curl $SERVICE_URL/hello/World
```

## Configuration

### Environment Variables

- `PORT`: The port the application runs on (default: 8080)

### Cloud Run Settings

The application is configured with:
- Memory: 512Mi
- CPU: 1
- Min instances: 0 (scales to zero)
- Max instances: 10
- Port: 8080

## Monitoring

The application includes a health check endpoint at `/health` that can be used for monitoring and load balancer health checks.

## Security

- The application runs as a non-root user in the container
- CORS is configured to allow all origins (adjust as needed for production)
- The service is deployed with unauthenticated access (add authentication as needed)

## Cost Optimization

- Configured to scale to zero when not in use
- Uses minimal resources (512Mi memory, 1 CPU)
- Efficient Docker image based on Python slim

## Troubleshooting

### Common Issues

1. **Port binding issues**: Ensure the application binds to `0.0.0.0:8080`
2. **Memory issues**: Increase memory allocation in Cloud Run settings
3. **Cold start delays**: Consider setting min-instances > 0 for production

### Logs

View logs using:
```bash
gcloud logs read --service=hello-world-api --limit=50
```

## License

MIT License

