from project.celery import app

from datetime import datetime

from web_parser.app.parser import WebParser


from celery import Task
from celery.utils.log import get_task_logger

task_logger = get_task_logger(__name__)
time_info = datetime.now()


class ProjectTask(Task):

    def run(self, *args, **kwargs):
        pass

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print(f"{task_id!r} failed: {exc!r}")


@app.task(bind=True, name='tasks.parse')
def parse_organisations(self):
    task_logger.info(f"-{time_info:%Y-%m-%d %H:%M:%S}-Executing task--id:{self.request.id}")
    try:
        WebParser.get_search_results()
    except Exception as ex:
        task_logger.warning(str(ex))
