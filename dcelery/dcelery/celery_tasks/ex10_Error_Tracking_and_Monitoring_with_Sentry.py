from sentry_sdk import capture_exception

from dcelery.celery_config import app

"""
from dcelery.celery_tasks.ex10_Error_Tracking_and_Monitoring_with_Sentry import divide_numbers
divide_numbers.delay(10, 0)
"""

@app.task(queue="tasks")
def divide_numbers(a,b):
    try:
        result = a / b
        return result
    except ZeroDivisionError as e:
        raise e