# Background Tasks

## Basic Background Task

```python
from fastapi import BackgroundTasks, FastAPI

app = FastAPI()

def write_notification(email: str, message: str = ""):
    with open("log.txt", "a") as log:
        log.write(f"Notification for {email}: {message}\n")

@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="Hello!")
    return {"message": "Notification sent in the background"}
```

## Multiple Background Tasks

```python
def send_email(email: str, message: str):
    # Simulated email sending
    print(f"Sending email to {email}: {message}")

def write_log(message: str):
    with open("log.txt", "a") as log_file:
        log_file.write(f"{message}\n")

@app.post("/send-notification/{email}")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email, email, "Welcome!")
    background_tasks.add_task(write_log, f"Email sent to {email}")
    return {"message": "Notification scheduled"}
```

## Background Tasks in Dependencies

```python
from typing import Annotated
from fastapi import BackgroundTasks, Depends

def write_log(message: str):
    with open("log.txt", "a") as log:
        log.write(message)

async def get_query(
    background_tasks: BackgroundTasks,
    q: str = None
):
    if q:
        background_tasks.add_task(write_log, f"Query: {q}\n")
    return q

@app.post("/items/")
async def create_item(query: Annotated[str, Depends(get_query)]):
    return {"query": query}
```

## Async Background Task

```python
import asyncio

async def send_email_async(email: str, message: str):
    await asyncio.sleep(2)  # Simulate async operation
    print(f"Email sent to {email}: {message}")

@app.post("/send-notification/")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email_async, email, "Welcome!")
    return {"message": "Notification scheduled"}
```

## When to Use Background Tasks

**Use BackgroundTasks when:**
- Sending email notifications
- Writing logs
- Small async operations
- Tasks that share memory/state with request

**Use Celery/Redis when:**
- Heavy computation
- Need to run on multiple servers
- Need task queues and retries
- Don't need shared memory

## Caveat from Official Docs

> If you need to perform heavy background computation and you don't necessarily
> need it to be run by the same process, you might benefit from using other
> bigger tools like Celery. They tend to require more complex configurations,
> a message/job queue manager, like RabbitMQ or Redis, but they allow you to
> run background tasks in multiple processes, and especially, in multiple servers.

## Background Task with Error Handling

```python
import logging

logger = logging.getLogger(__name__)

def process_file(file_path: str):
    try:
        # Process file
        with open(file_path) as f:
            data = f.read()
        # Do something with data
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")

@app.post("/process/")
async def process_upload(
    file_path: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(process_file, file_path)
    return {"message": "Processing started"}
```
