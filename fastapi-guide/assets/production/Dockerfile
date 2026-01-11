FROM python:3.11-slim

WORKDIR /code

# Install dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy application
COPY ./app /code/app

# Run with multiple workers for production
CMD ["fastapi", "run", "app/main.py", "--port", "80", "--workers", "4"]
