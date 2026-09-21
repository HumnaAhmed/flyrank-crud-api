from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI()


class TaskCreate(BaseModel):
    title: str = Field(min_length=1)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    done: bool | None = None


tasks = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Build a CRUD API", "done": False},
    {"id": 3, "title": "Write the README", "done": True},
]


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid request body"}
    )


@app.get(
    "/",
    description="Show basic information about the Task API."
)
def home():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get(
    "/health",
    description="Check whether the API is running."
)
def health():
    return {
        "status": "ok"
    }


@app.get(
    "/tasks",
    description="Return all tasks."
)
def get_tasks():
    return tasks


@app.get(
    "/tasks/{task_id}",
    description="Return one task by ID."
)
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task

    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )


@app.post(
    "/tasks",
    status_code=status.HTTP_201_CREATED,
    description="Create a new task."
)
def create_task(task_data: TaskCreate):
    next_id = max(
        (task["id"] for task in tasks),
        default=0
    ) + 1

    new_task = {
        "id": next_id,
        "title": task_data.title,
        "done": False
    }

    tasks.append(new_task)

    return new_task


@app.put(
    "/tasks/{task_id}",
    description="Update a task by ID."
)
def update_task(task_id: int, task_data: TaskUpdate):
    for task in tasks:
        if task["id"] == task_id:
            updates = task_data.model_dump(
                exclude_unset=True
            )

            if not updates:
                raise HTTPException(
                    status_code=400,
                    detail="Update body cannot be empty"
                )

            if "title" in updates and updates["title"] is None:
                raise HTTPException(
                    status_code=400,
                    detail="Title cannot be empty"
                )

            if "done" in updates and updates["done"] is None:
                raise HTTPException(
                    status_code=400,
                    detail="Done must be a boolean"
                )

            task.update(updates)

            return task

    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete a task by ID."
)
def delete_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return

    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )