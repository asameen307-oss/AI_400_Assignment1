from fastapi import FastAPI,Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session, select,Field
from typing import List,Dict


app=FastAPI(title="Task Management API",version="1.0.0")

def get_config():
    load_dotenv()
    DATABASE_URL=os.getenv("DB_CONN_STRING","sqlite:///./test.db")
    return {
        "DATABASE_URL": DATABASE_URL,"AppName":"TaskManagementAPI","Version":"1.0.0"
    }

config=get_config()
engine = create_engine(config["DATABASE_URL"],echo=True)

class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    description: str 
    completed: bool 

def create_db_and_tables(config: dict = Depends(get_config)):
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session


@app.post("/tasks/", response_model=Task)
def create_task(task: Task, session=Depends(get_session)):
    session.add(task)
    session.commit()
    session.refresh(task)
    return {'message': 'Task created successfully', 'task': task}

@app.get("/tasks/", response_model=List[Task])
def read_tasks(session=Depends(get_session)):
    tasks = session.exec(select(Task)).all()
    return tasks

@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: int, session=Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        return HTTPException(status_code=404, detail="Task not found")
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session=Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        return HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"message": "Task deleted successfully"}

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: Task, session=Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        return HTTPException(status_code=404, detail="Task not found")
    task.title = updated_task.title
    task.description = updated_task.description
    task.completed = updated_task.completed
    session.add(task)
    session.commit()
    session.refresh(task)
    return task 