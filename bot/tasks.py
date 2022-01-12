import os
import logging

from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

from slack_sdk import WebClient
from db import DB

SEC = 1
MIN = 60
HR = 3600

class TaskManager(object):
    def __init__(self):
        self.logger = logging.getLogger('tasks')

        self.scheduler = BackgroundScheduler(
            jobstores = {
                'default': MemoryJobStore()
            },
            executors = {
                'default': ThreadPoolExecutor(10),
            },
            job_defaults = {
                'coalesce': False,
                'max_instances': 1
            })

        self.scheduler.start()

        self.tasks = {
            'update_users_info': {
                'func': self.update_users_info,
                'type': 'interval',
                'interval': 24 * HR
            }
        }

        for task_name in self.tasks:
            task_spec = self.tasks[task_name]
            task_type = task_spec['type']
            task_func = task_spec['func']

            if task_type == 'interval':
                interval = task_spec['interval']

                self.scheduler.add_job(task_func, 'interval',
                                       seconds = interval,
                                       id = task_name,
                                       next_run_time = datetime.now())

    def update_users_info(self):
        self.logger.info(f'Updating users info')
        db = DB()
        client = WebClient(os.environ["SLACK_BOT_TOKEN"])

        user_ids = db.get_all_user_ids()
        user_info = {}

        for user_id in user_ids:
            user_info[user_id] = {}

            try:
                info = client.users_info(user = user_id)
            except Exception as ex:
                self.logger.error(f'users_info failed: {ex}')

            try:
                avatar_url = info['user']['profile']['image_32']
            except:
                avatar_url = '?'

            try:
                name = info['user']['profile']['display_name']
                if name == '':
                    name = info['user']['profile']['real_name']
            except:
                name = '?'

            db.update_user_info(user_id, name, avatar_url)

        db.close()
