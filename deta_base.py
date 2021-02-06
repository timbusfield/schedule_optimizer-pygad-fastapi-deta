from deta import Deta

deta = Deta()
taskset_db = deta.Base("taskset_db")


def create_taskset(taskset):
    put_result = taskset_db.put(taskset.dict())
    return put_result


def get_taskset(taskset_key):
    found_taskset = taskset_db.get(taskset_key)
    return found_taskset
