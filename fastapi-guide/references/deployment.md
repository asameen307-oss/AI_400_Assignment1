# Deployment

## Docker Deployment (Recommended)

### Basic Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["fastapi", "run", "app/main.py", "--port", "80"]
```

### Production Dockerfile with Workers

```dockerfile
FROM python:3.11-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

# Multiple workers for production
CMD ["fastapi", "run", "app/main.py", "--port", "80", "--workers", "4"]
```

### Dockerfile with Proxy Headers (Behind Nginx/Traefik)

```dockerfile
FROM python:3.11-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["fastapi", "run", "app/main.py", "--port", "80", "--proxy-headers"]
```

### Build and Run

```bash
# Build image
docker build -t myapp .

# Run container
docker run -d -p 80:80 myapp

# Run with environment variables
docker run -d -p 80:80 \
  -e DATABASE_URL="postgresql://..." \
  -e SECRET_KEY="your-secret" \
  myapp
```

### Docker Compose

```yaml
# docker-compose.yml
version: "3.8"

services:
  web:
    build: .
    ports:
      - "80:80"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/app
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=app
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Uvicorn Direct Deployment

### Development
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### With fastapi CLI
```bash
# Development (auto-reload)
fastapi dev app/main.py

# Production
fastapi run app/main.py --workers 4
```

## Worker Count Recommendation

From official docs:
> Use multiple workers to utilize multiple CPU cores. A common formula is
> `(2 x num_cores) + 1` workers.

```bash
# Example for 4-core machine
fastapi run app/main.py --workers 9
```

## Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/myapp
upstream app_server {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://app_server;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Systemd Service

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=FastAPI Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/home/app/myapp
Environment="PATH=/home/app/myapp/venv/bin"
ExecStart=/home/app/myapp/venv/bin/fastapi run app/main.py --port 8000 --workers 4

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl start myapp
sudo systemctl enable myapp
```

## Cloud Deployments

### AWS (ECS/Fargate)

```json
{
  "containerDefinitions": [
    {
      "name": "fastapi-app",
      "image": "your-ecr-repo/myapp:latest",
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "DATABASE_URL", "value": "..."},
        {"name": "SECRET_KEY", "value": "..."}
      ]
    }
  ]
}
```

### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/myapp

# Deploy
gcloud run deploy myapp \
  --image gcr.io/PROJECT_ID/myapp \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="DATABASE_URL=..."
```

### Azure Container Apps

```bash
az containerapp create \
  --name myapp \
  --resource-group mygroup \
  --environment myenv \
  --image myregistry.azurecr.io/myapp:latest \
  --target-port 80 \
  --ingress external \
  --env-vars DATABASE_URL=...
```

## HTTPS with Traefik

```yaml
# docker-compose.yml with Traefik
version: "3.8"

services:
  traefik:
    image: traefik:v2.10
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.myresolver.acme.httpchallenge.entrypoint=web"
      - "--certificatesresolvers.myresolver.acme.email=admin@example.com"
      - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "./letsencrypt:/letsencrypt"

  web:
    build: .
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.web.rule=Host(`example.com`)"
      - "traefik.http.routers.web.entrypoints=websecure"
      - "traefik.http.routers.web.tls.certresolver=myresolver"
```

## Health Check Endpoint

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

## Deprecated: Base Docker Image

From official docs:
> The official FastAPI Docker base image (tiangolo/uvicorn-gunicorn-fastapi)
> is now deprecated and should not be used. Build your own image from the
> official Python Docker image instead.
