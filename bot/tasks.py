import os
import logging
import time

from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

from slack_sdk import WebClient
from db import DB
from strings import *

SEC = 1
MIN = 60
HR = 3600

def ts_to_str(ts):
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')


class TaskManager(object):
    def __init__(self, bot):
        self.bot = bot
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
            },
            'bets_reminder': {
                'func': self.bets_reminder,
                'type': 'cron',
                'cron_args': {
                    'day_of_week': 'sun',
                    'hour': 20,
                    'minute': 0
                }
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
            elif task_type == 'cron':
                cron_args = task_spec['cron_args']

                self.scheduler.add_job(task_func, 'cron',
                                       **cron_args)


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


    def bets_reminder(self):
        db = DB()

        results = db.get_bets()
        ALIGN_ID = 5
        ALIGN_DATE = 22
        MAX_TEXT = 2900

        truncated = False

        text = '{} {} {}\n'.format(
            'Id'.ljust(ALIGN_ID),
            'Voting ends on'.ljust(ALIGN_DATE+7),
            'Question')
        text += '-' * 50 + '\n'

        now = int(time.time())

        send_reminder = False

        for bet_id, resolve_date_ts, voting_end_date_ts, question, active, _ in results:
            if not active:
                continue

            if now > voting_end_date_ts:
                continue

            line = '{} {} {}\n'.format(
                str(bet_id).ljust(ALIGN_ID),
                ts_to_str(voting_end_date_ts).ljust(ALIGN_DATE),
                question.split('\n')[0])

            if len(text) + len(line) > MAX_TEXT:
                truncated = True
                break

            text += line

            send_reminder = True

        if send_reminder:
            self.bot.do_reply_on_channel(self.bot.rtm, None, self.bot.my_channel,
                                         bets_reminder_blocks(text, truncated),
                                         'Bets reminder')

