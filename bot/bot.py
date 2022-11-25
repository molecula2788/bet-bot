import os
import logging
import time
import re
import shlex
import config
from datetime import datetime
from typing import List

from slack_sdk.rtm_v2 import RTMClient

from db import DB
from strings import *
from tasks import TaskManager

MENTION_REGEX = '^<@([WU].+)>(.*)'

MAX_QUESTION_LEN = 255
MAX_ANSWER_LEN = 255

def ts_to_str(ts):
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')


class Bot(object):
    def __init__(self):
        self.db = DB()
        self.rtm = RTMClient(token=os.environ['SLACK_BOT_TOKEN'])

        self._rtm_on('message')(self.on_message)
        self._rtm_on('member_joined_channel')(self.on_joined_channel)

        self.my_channel = self.db.config_get_channel()
        self.admin_user_id = self.db.config_get_admin_user_id()
        self.my_user_id = self.rtm.web_client.auth_test()['user_id']

        self.task_mgr = TaskManager()

        self.logger = logging.getLogger('bot')


    def _rtm_on(self, ev_type: str):
        def tmp(func):
            def handler(client, event):
                func(client, event)
            self.rtm.on(ev_type)(handler)
        return tmp


    def get_user_info(self, user_id: str):
        res = self.db.get_user_info(user_id)

        if not res:
            try:
                info = self.rtm.web_client.users_info(user = user_id)
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

            self.db.update_user_info(user_id, name, avatar_url)
        else:
            name, avatar_url = res

        return name, avatar_url


    def parse_direct_mention(self, message_text: str):
        matches = re.search(MENTION_REGEX, message_text)
        # the first group contains the username, the second group contains the remaining message
        return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


    def do_reply_ephemeral(self, client: RTMClient, event: dict,
                           message_blocks: dict, message_text: str):
        channel = event.get('channel', None)
        user_id = event.get('user', None)
        thread_ts = event.get('thread_ts', None)

        if not channel or not user_id:
            return

        try:
            client.web_client.chat_postEphemeral(
                channel = channel,
                user = user_id,
                thread_ts = thread_ts,
                blocks = message_blocks,
                text = message_text
            )
        except Exception as ex:
            self.logger.error(f'chat_postEphemeral failed: {ex}')


    def do_reply(self, client: RTMClient, event: dict,
                 message_blocks: dict, message_text: str):
        channel = event.get('channel', None)
        user_id = event.get('user', None)
        thread_ts = event.get('thread_ts', None)

        if not channel or not user_id:
            return

        try:
            client.web_client.chat_postMessage(
                channel = channel,
                user = user_id,
                thread_ts = thread_ts,
                blocks = message_blocks,
                text = message_text
            )
        except Exception as ex:
            self.logger.error(f'chat_postMessage failed: {ex}')


    def do_reply_on_channel(self, client: RTMClient, event: dict,
                            channel: str, message_blocks: dict, message_text: str):
        try:
            client.web_client.chat_postMessage(
                channel = channel,
                blocks = message_blocks,
                text = message_text
            )
        except Exception as ex:
            self.logger.error(f'chat_postMessage failed: {ex}')


    def do_reply_big_msg(self, client: RTMClient, event: dict,
                         title: str, comment: str, text: str):
        try:
            res = client.web_client.conversations_open(users = event['user'])
        except Exception as ex:
            self.logger.error(f'conversations_open failed: {ex}')

        channel = res['channel']['id']

        try:
            client.web_client.files_upload(
                channels = channel,
                content = text,
                title = title,
                initial_comment = comment)
        except Exception as ex:
            self.logger.error(f'files_upload failed: {ex}')


    '''
    help
    '''
    def help(self, client: RTMClient, event: dict, args: List[str]):
        self.do_reply(client, event, help_blocks, 'help')


    '''
    bets
    '''
    def bets(self, client: RTMClient, event: dict, args: List[str]):
        results = self.db.get_bets()
        ALIGN_ID = 5
        ALIGN_DATE = 22
        MAX_TEXT = 2900

        truncated = False

        text = '{} {} {}\n'.format(
            'Id'.ljust(ALIGN_ID),
            'Voting ends on'.ljust(ALIGN_DATE+7),
            'Question')
        text += '-' * 50 + '\n'

        now = time.time()

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

        self.do_reply(client, event,
                      bets_blocks(text, truncated),
                      'Bets')

    '''
    bets-all
    '''
    def bets_all(self, client: RTMClient, event: dict, args: List[str]):
        ALIGN_ID = 10
        ALIGN_DATE = 25
        ALIGN_QUESTION = 75
        ALIGN_ANSWER = 50

        results = self.db.get_bets()
        text = 'Ongoing\n\n'
        text += '{} {} {} {}\n'.format(
            'Id'.ljust(ALIGN_ID),
            'Resolve date'.ljust(ALIGN_DATE),
            'Voting ends on'.ljust(ALIGN_DATE),
            'Question')
        text += '-' * 75 + '\n'

        now = int(time.time())

        for bet_id, resolve_date_ts, voting_end_date_ts, question, active, _ in results:
            if active and now <= voting_end_date_ts:
                question = question.split('\n')[0]
                text += '{} {} {} {}\n'.format(
                    '{}'.format(bet_id).ljust(ALIGN_ID),
                    ts_to_str(resolve_date_ts).ljust(ALIGN_DATE),
                    ts_to_str(voting_end_date_ts).ljust(ALIGN_DATE),
                    question[:ALIGN_QUESTION])

        text += '\nVoting ended\n\n'
        text += '{} {} {} {}\n'.format(
            'Id'.ljust(ALIGN_ID),
            'Resolve date'.ljust(ALIGN_DATE),
            'Voting ended on'.ljust(ALIGN_DATE),
            'Question')
        text += '-' * 75 + '\n'

        for bet_id, resolve_date_ts, voting_end_date_ts, question, active, _ in results:
            if active and now > voting_end_date_ts:
                question = question.split('\n')[0]
                text += '{} {} {} {}\n'.format(
                    '{}'.format(bet_id).ljust(ALIGN_ID),
                    ts_to_str(resolve_date_ts).ljust(ALIGN_DATE),
                    ts_to_str(voting_end_date_ts).ljust(ALIGN_DATE),
                    question[:ALIGN_QUESTION])


        text += '\nPast bets\n\n'
        text += '{} {} {} {} {}\n'.format(
            'Id'.ljust(ALIGN_ID),
            'Resolve date'.ljust(ALIGN_DATE),
            'Voting ended on'.ljust(ALIGN_DATE),
            'Question'.ljust(ALIGN_QUESTION),
            'Correct choice')
        text += '-' * 160 + '\n'

        for bet_id, resolve_date_ts, voting_end_date_ts, question, active, correct_choice in results:
            if not active:
                question = question.split('\n')[0]
                text += '{} {} {} {} {}\n'.format(
                    '{}'.format(bet_id).ljust(ALIGN_ID),
                    ts_to_str(resolve_date_ts).ljust(ALIGN_DATE),
                    ts_to_str(voting_end_date_ts).ljust(ALIGN_DATE),
                    question[:ALIGN_QUESTION].ljust(ALIGN_QUESTION),
                    correct_choice[:ALIGN_ANSWER])

        text = text[:-1]

        comment = f'Use `@{config.my_name} bet-info id` for more details'
        title = 'All bets'

        self.do_reply_big_msg(client, event, title, comment, text)


    '''
    my-bets
    '''
    def my_bets(self, client: RTMClient, event: dict, args: List[str]):
        ALIGN_ID = 10
        ALIGN_DATE = 25
        ALIGN_QUESTION = 75
        ALIGN_ANSWER = 50
        ALIGN_CORRECT_ANSWER = 50

        results = self.db.get_bets_for_user(event['user'])

        text = 'Ongoing\n\n'
        text += '{} {} {} {} {}\n'.format(
            'Id'.ljust(ALIGN_ID),
            'Resolve date'.ljust(ALIGN_DATE),
            'Voting ends on'.ljust(ALIGN_DATE),
            'Question'.ljust(ALIGN_QUESTION),
            'Your choice')
        text += '-' * 180 + '\n'

        now = int(time.time())

        for bet_id, resolve_date_ts, voting_end_date_ts, active, question, correct_choice, choice in results:
            if active and now <= voting_end_date_ts:
                question = question.split('\n')[0]

                text += '{} {} {} {} {}\n'.format(
                    '{}'.format(bet_id).ljust(ALIGN_ID),
                    ts_to_str(resolve_date_ts).ljust(ALIGN_DATE),
                    ts_to_str(voting_end_date_ts).ljust(ALIGN_DATE),
                    question[:ALIGN_QUESTION].ljust(ALIGN_QUESTION),
                    choice[:ALIGN_ANSWER])

        text += '\nVoting ended\n\n'
        text += '{} {} {} {}\n'.format(
            'Id'.ljust(ALIGN_ID),
            'Resolve date'.ljust(ALIGN_DATE),
            'Voting ended on'.ljust(ALIGN_DATE),
            'Question'.ljust(ALIGN_QUESTION),
            'Your choice')
        text += '-' * 180 + '\n'

        for bet_id, resolve_date_ts, voting_end_date_ts, active, question, correct_choice, choice in results:
            if active and now > voting_end_date_ts:
                question = question.split('\n')[0]

                text += '{} {} {} {} {}\n'.format(
                    '{}'.format(bet_id).ljust(ALIGN_ID),
                    ts_to_str(resolve_date_ts).ljust(ALIGN_DATE),
                    ts_to_str(voting_end_date_ts).ljust(ALIGN_DATE),
                    question[:ALIGN_QUESTION].ljust(ALIGN_QUESTION),
                    choice[:ALIGN_ANSWER])

        text += '\nPast bets\n\n'
        text += '{} {} {} {} {} {}\n'.format(
            'Id'.ljust(ALIGN_ID),
            'Resolve date'.ljust(ALIGN_DATE),
            'Voting ended on'.ljust(ALIGN_DATE),
            'Question'.ljust(ALIGN_QUESTION),
            'Your choice'.ljust(ALIGN_ANSWER),
            'Correct choice')
        text += '-' * 210 + '\n'

        for bet_id, resolve_date_ts, voting_end_date_ts, active, question, correct_choice, choice in results:
            if not active:
                question = question.split('\n')[0]
                text += '{} {} {} {} {} {}\n'.format(
                    '{}'.format(bet_id).ljust(ALIGN_ID),
                    ts_to_str(resolve_date_ts).ljust(ALIGN_DATE),
                    ts_to_str(voting_end_date_ts).ljust(ALIGN_DATE),
                    question[:ALIGN_QUESTION].ljust(ALIGN_QUESTION),
                    choice[:ALIGN_ANSWER].ljust(ALIGN_ANSWER),
                    correct_choice[:ALIGN_CORRECT_ANSWER])

        text = text[:-1]

        comment = f'Use `@{config.my_name} bet-info id` for more details'
        title = 'Bets you\'ve taken part in'

        self.do_reply_big_msg(client, event, title, comment, text)


    '''
    bet_info id
    '''
    def bet_info(self, client: RTMClient, event: dict, args: List[str]):
        if len(args) != 1 or args[0] == 'help':
            self.do_reply(client, event,
                          usage_bet_info_blocks,
                          usage_bet_info_text)
            return

        bet_id = args[0]

        try:
            info, choices = self.db.bet_info(bet_id)
        except Exception as ex:
            self.logger.error(f'bet_info failed: {ex}')
            return

        if info is None:
            self.do_reply(client, event,
                          bet_not_found_blocks,
                          bet_not_found_text)
            return

        active, _, resolve_date_ts, voting_end_date_ts, correct_choice_id, question = info

        try:
            votes = self.db.bet_get_votes(bet_id)
        except Exception as ex:
            self.logger.error(f'bet_get_votes failed: {ex}')
            return

        user_info = {}

        for choice_id in votes:
            for user_id, _ in votes[choice_id]:
                name, avatar_url = self.get_user_info(user_id)

                user_info[user_id] = { 'name': name, 'avatar_url': avatar_url }

        self.do_reply(client, event,
                      bet_info_blocks(bet_id, question, choices, correct_choice_id,
                                      resolve_date_ts, voting_end_date_ts, votes, user_info),
                      bet_info_text)


    '''
    bet_vote bet_id choice
    '''
    def bet_vote(self, client: RTMClient, event: dict, args: List[str]):
        if len(args) == 1 and args[0] == 'help':
            self.do_reply(client, event,
                          usage_bet_vote_blocks, usage_bet_vote_text)
            return

        if len(args) < 2:
            self.do_reply(client, event,
                          usage_bet_vote_blocks, usage_bet_vote_text)
            return

        bet_id = args[0]
        choice = args[1]

        try:
            info, choices = self.db.bet_info(bet_id)
        except Exception as ex:
            self.logger.error(f'bet_info failed: {ex}')
            return

        if info is None:
            self.do_reply(client, event,
                          bet_not_found_blocks,
                          bet_not_found_text)
            return

        active, _, _, voting_end_date_ts, correct_choice_id, question = info

        if not active:
            self.do_reply(client, event,
                          None,
                          bet_not_active_text)
            return

        vote_ts = int(time.time())
        if vote_ts > voting_end_date_ts:
            self.do_reply(client, event,
                          None,
                          bet_vote_has_ended)
            return

        try:
            choice_idx = int(choice, 10)
            choice_idx -= 1
            if choice_idx < 0 or choice_idx >= len(choices):
                raise Exception('Invalid choice')
        except:
            self.do_reply(client, event,
                          invalid_choice_blocks(choice),
                          invalid_choice_text(choice))
            return

        try:
            result = self.db.bet_do_vote(bet_id, event['user'], vote_ts, choices[choice_idx][0])
        except Exception as ex:
            self.logger.error(f'bet_do_vote failed: {ex}')
            return

        self.do_reply(client, event,
                      vote_registered_blocks(question.split('\n')[0], choices[choice_idx][1]),
                      vote_registered_text)


    '''
    bet_create resolve_date end_vote_date question choice1 choice2 ...
    '''
    def bet_create(self, client: RTMClient, event: dict, args: List[str]):
        if len(args) < 4:
            self.do_reply(client, event, usage_bet_create_blocks, usage_bet_create_text)
            return

        if len(args) == 1 and args[0] == 'help':
            self.do_reply(client, event, usage_bet_create_blocks, usage_bet_create_text)
            return

        resolve_date = args[0]
        end_vote_date = args[1]
        question = args[2]
        choices = args[3:]

        question = question.replace('\\n', '\n')

        question = question[:MAX_QUESTION_LEN]
        choices = [c[:MAX_ANSWER_LEN] for c in choices]

        try:
            resolve_date_ts = int(datetime.fromisoformat(resolve_date).timestamp())
        except:
            resolve_date_ts = None

        if not resolve_date_ts:
            self.do_reply(client, event, None, f'Invalid date: {resolve_date}')
            return

        try:
            voting_end_date_ts = int(datetime.fromisoformat(end_vote_date).timestamp())
        except:
            voting_end_date_ts = None

        if not voting_end_date_ts:
            self.do_reply(client, event, None, f'Invalid date: {end_vote_date}')
            return

        if voting_end_date_ts > resolve_date_ts:
            self.do_reply(client, event, None, f'End vote date ({end_vote_date}) cannot be later than resolve date ({resolve_date})')
            return

        try:
            bet_id = self.db.bet_create(event['user'], int(datetime.now().timestamp()),
                                        resolve_date_ts, voting_end_date_ts, question, choices)
        except Exception as ex:
            self.logger.error(f'bet_create failed: {ex}')
            return

        self.do_reply_on_channel(client, event, self.my_channel,
                                 bet_created_blocks(bet_id, question.split('\n')[0], event['user']),
                                 bet_created_text(bet_id, question))


    '''
    bet_resolve bet_id choice
    '''
    def bet_resolve(self, client: RTMClient, event: dict, args: List[str]):
        if len(args) != 2:
            self.do_reply(client, event, usage_bet_resolve_blocks, usage_bet_resolve_text)
            return

        if len(args) == 1 and args[0] == 'help':
            self.do_reply(client, event, usage_bet_resolve_blocks, usage_bet_resolve_text)
            return

        bet_id = args[0]
        choice = args[1]

        try:
            info, choices = self.db.bet_info(bet_id)
        except Exception as ex:
            self.logger.error(f'bet_info failed: {ex}')
            return

        if info is None:
            self.do_reply(client, event,
                          bet_not_found_blocks,
                          bet_not_found_text)
            return

        active, bet_owner, _, voting_end_date_ts, _, question = info

        if event['user'] != self.admin_user_id and event['user'] != bet_owner:
            return

        if not active:
            self.do_reply(client, event,
                          None,
                          bet_not_active_text)
            return

        if int(time.time()) < voting_end_date_ts:
            self.do_reply(client, event,
                          None,
                          bet_vote_not_ended)
            return

        try:
            choice_idx = int(choice, 10)
            choice_idx -= 1
            if choice_idx < 0 or choice_idx >= len(choices):
                raise Exception('Invalid choice')
        except:
            self.do_reply(client, event,
                          invalid_choice_blocks(choice),
                          invalid_choice_text(choice))
            return

        try:
            result = self.db.bet_resolve(bet_id, choices[choice_idx][0])
        except Exception as ex:
            self.logger.error(f'bet_resolve failed: {ex}')
            return

        try:
            winners = self.db.get_winners(bet_id)
        except Exception as ex:
            self.logger.error(f'get_winners failed: {ex}')
            return

        self.do_reply_on_channel(client, event, self.my_channel,
                                 bet_resolved_blocks(bet_id, question, choices[choice_idx][1], winners),
                                 bet_resolved_text(bet_id, question, choices[choice_idx][1]))


    def on_message(self, client: RTMClient, event: dict):
        if 'subtype' in event:
            return

        if not 'text' in event:
            return

        if not 'user' in event:
            return

        mention_user_id, message = self.parse_direct_mention(event['text'])
        if not mention_user_id or mention_user_id != self.my_user_id:
            return

        words = shlex.split(message)

        if len(words) == 0:
            return

        cmd = words[0]
        args = words[1:]

        if cmd == 'help':
            self.help(client, event, args)
        elif cmd == 'bets':
            self.bets(client, event, args)
        elif cmd == 'bets-all':
            self.bets_all(client, event, args)
        elif cmd == 'my-bets':
            self.my_bets(client, event, args)
        elif cmd == 'bet-info':
            self.bet_info(client, event, args)
        elif cmd == 'vote':
            self.bet_vote(client, event, args)
        elif cmd == 'bet-create':
            self.bet_create(client, event, args)
        elif cmd == 'bet-resolve':
            self.bet_resolve(client, event, args)


    def on_joined_channel(self, client: RTMClient, event: dict):
        if event['channel'] != self.my_channel:
            return

        self.do_reply_on_channel(client, event, self.my_channel,
                                 user_joined_blocks(event['user']),
                                 '')

    def start(self):
        self.rtm.start()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    time.sleep(2)

    bot = Bot()
    bot.start()
