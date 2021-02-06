from deta import Deta
from datetime import datetime, timedelta

deta = Deta()
taskset_db = deta.Base("taskset_db")
optimization_db = deta.Base("optimization_db")

DATETIME_STRING_FORMAT = "%Y-%m-%dT%H:%M:%S"

def create_taskset(taskset):
    put_result = taskset_db.put(taskset.dict())
    return put_result


def get_taskset(taskset_key):
    found_taskset = taskset_db.get(taskset_key)
    return found_taskset


def optimization_requested_record(taskset_key, optimization_parameters):
    record = {
        "taskset_key": taskset_key,
        "request_time": datetime.now().strftime(DATETIME_STRING_FORMAT),
        "status": "Requested",
        "parameters": optimization_parameters.dict(),
    }
    put_result = optimization_db.put(record)
    return put_result


def optimization_completed_record(taskset_key, optimization_parameters,
                                  scheduled_tasks, solution_fitness):
    record = {
        "taskset_key": taskset_key,
        "request_time": datetime.now().strftime(DATETIME_STRING_FORMAT),
        "status": "Completed",
        "parameters": optimization_parameters.dict(),
        "scheduled_tasks": scheduled_tasks,  # being passed as an object at the moment, this should change
        "solution_fitness": solution_fitness
    }
    put_result = optimization_db.put(record)
    return put_result
