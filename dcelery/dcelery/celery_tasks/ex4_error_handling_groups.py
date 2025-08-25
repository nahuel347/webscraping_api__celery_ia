from celery import group

from dcelery.celery_config import app

"""
from dcelery.celery_tasks.ex4_error_handling_groups import run_tasks
run_tasks()
"""

@app.task(queue='tasks')
def my_task(number):

    if number == 3:
        raise ValueError("Error Number is Invalid")
    return number * 2

def handle_result(result):
    if result.successful():
        print(f"Task Completed:{result.get()}")
    elif result.failed() and isinstance(result.result, ValueError):
        print(f"Task failed: {result.result}")
    elif result.status == 'REVOKED':
        print(f"Task was revoked: {result.id}")

def run_tasks():
    task_group = group(my_task.s(i) for i in range(5))
    result_group = task_group.apply_async()
    result_group.get(disable_sync_subtasks=False,propagate=False)

    for result in result_group:
        handle_result(result)