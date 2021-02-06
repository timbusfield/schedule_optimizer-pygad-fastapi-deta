from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from deta_base import create_taskset, get_taskset
from deta_base import optimization_requested_record, optimization_completed_record
from optimizer import run_optimization

app = FastAPI()


class Task(BaseModel):
    task_id: str
    duration: int
    people: int
    task_prerequisites: Optional[List[str]] = None


class ScheduledTask(Task):
    start: int
    end: int


class TaskSet(BaseModel):
    name: str
    tasks: List[Task]


class TaskSetKey(TaskSet):
    key: str


class OptimizationParameters(BaseModel):
    max_people: int
    population_size: Optional[int] = 50
    number_generations: Optional[int] = 100
    number_parents_mating: Optional[int] = 10
    parent_selection_type: Optional[str] = "sss"
    keep_parents: Optional[int] = -1
    crossover_type: Optional[str] = "single_point"
    mutation_type: Optional[str] = "random"
    mutation_percent_genes: Optional[int] = 10


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/taskset")
def create_taskset_api(taskset: TaskSet):
    result = create_taskset(taskset)
    if "key" not in result.keys():
        raise HTTPException(status_code=400, detail="Item not created")
    return result["key"]


@app.get("/taskset/{taskset_key}")
def get_taskset_api(taskset_key: str):
    result = get_taskset(taskset_key)
    if result is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return result


@app.post("/optimize/{taskset_key}")
def run_optimization_api(taskset_key: str, optimization_parameters: OptimizationParameters):
    taskset = get_taskset(taskset_key)
    if taskset is None:
        raise HTTPException(status_code=404, detail="Item not found")
    taskset = TaskSetKey.parse_obj(taskset)
    optimization_requested_record(taskset.key, optimization_parameters)
    result = run_optimization(
        taskset.tasks,
        optimization_parameters
    )
    optimization_completed_record(
        taskset.key, optimization_parameters,
        result["scheduled_tasks"], result["outcome"]["solution_fitness"])
    return "Completed"
