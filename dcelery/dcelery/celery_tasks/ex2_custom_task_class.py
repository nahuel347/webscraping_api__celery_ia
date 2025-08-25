import logging

from celery import Task

from dcelery.celery_config import app

"""
from dcelery.celery_tasks.ex2_custom_task_class import my_task
my_task.delay()
"""

logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(actime)s %(levelname)s %(message)s')

class CustomTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if isinstance(exc, ConnectionError):
            logging.error('Connection error occurred - Admin Notified')
        else:
            print('{0!r} failed: {1!r}'.format(task_id, exc))
            # Perform additional error handling actions if needed

app.Task = CustomTask

@app.task(queue='tasks')
def my_task():
    try:
        raise ConnectionError("Connection Error Occurred...")
    except ConnectionError:
        raise ConnectionError()
    except ValueError:
        # Handle value error
        logging.error('Value error occurred...')
        # Perform specific error handling actions
        perform_specific_error_handling()
    except Exception:
        # Handle generic exceptions
        logging.error('An error occurred')
        # Notify administrators or perform fallback action
        notify_admins()
        perform_fallback_action()

def perform_specific_error_handling():
    # Logic to handle a specific error scenario
    pass

def notify_admins():
    # Logic to send notifications to administrators
    pass

def perform_fallback_action():
    # Logic to perform fallback action when an error occurs
    pass