import os
import time
import mysql.connector

class DB(object):
    def __init__(self):
        host = os.environ.get('MYSQL_HOST', None)
        if not host:
            raise Exception('MYSQL_HOST environment variable not set')

        user = os.environ.get('MYSQL_USER', None)
        if not user:
            raise Exception('MYSQL_USER environment variable not set')

        password = os.environ.get('MYSQL_PASSWORD', None)
        if not password:
            raise Exception('MYSQL_PASSWORD environment variable not set')

        db = os.environ.get('MYSQL_DATABASE', None)
        if not db:
            raise Exception('MYSQL_DATABASE environment variable not set')

        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db
        )


    def ensure_connected(self):
        self.conn.ping(reconnect=True, attempts=3)


    def close(self):
        self.conn.close()


    def config_get_channel(self):
        cursor = self.conn.cursor()

        cursor.execute("SELECT value FROM bot_config WHERE name = 'channel_id'")

        result = list(cursor.fetchall())

        assert(len(result) == 1)

        return result[0][0]


    def bet_create(self, user_id, ts, resolve_date_ts, question, choices):
        self.ensure_connected()
        cursor = self.conn.cursor(prepared=True)

        cursor.execute(('INSERT INTO bets (user, ts, resolve_date, active) '
                        'VALUES (%s, %s, %s, 1)'),
                       (user_id, ts, resolve_date_ts))

        bet_id = cursor.lastrowid

        cursor.execute(('INSERT INTO bet_questions (bet_id, question) '
                        'VALUES (%s, %s)'),
                       (bet_id, question))

        cursor.executemany(('INSERT INTO bet_choices (bet_id, choice) '
                            'VALUES (%s, %s)'),
                            [(bet_id, a) for a in choices])


        self.conn.commit()
        cursor.close()

        return bet_id


    def bet_info(self, bet_id):
        self.ensure_connected()
        cursor = self.conn.cursor(prepared=True)

        cursor.execute(
            ('SELECT b.active, b.user, b.resolve_date, b.correct_choice_id, q.question FROM bets b '
             'INNER JOIN bet_questions q ON b.id = q.bet_id '
             'WHERE b.id = %s '),
            (bet_id,))

        info = list(cursor.fetchall())

        if len(info) == 0:
            self.conn.commit()
            cursor.close()

            return None, None, None

        info = info[0]

        cursor.execute(
            ('SELECT c.id, c.choice FROM bet_choices c '
             'INNER JOIN bets b ON b.id = c.bet_id '
             'WHERE b.id = %s '
             'ORDER BY c.id'),
            (bet_id,))

        choices = list(cursor.fetchall())

        self.conn.commit()
        cursor.close()

        return (info, choices)


    def bet_get_votes(self, bet_id):
        self.ensure_connected()
        cursor = self.conn.cursor(prepared=True)

        cursor.execute(('SELECT v.user, v.choice_id, v.ts FROM bets b '
                        'INNER JOIN bet_votes v ON b.id = v.bet_id '
                        'WHERE b.id = %s'),
                       (bet_id,))

        votes = {}

        result = cursor.fetchall()
        for user, choice_id, ts in result:
            if choice_id in votes:
                votes[choice_id].append((user, ts))
            else:
                votes[choice_id] = [(user, ts)]

        self.conn.commit()
        cursor.close()

        return votes


    def bet_do_vote(self, bet_id, user_id, choice_id):
        self.ensure_connected()
        cursor = self.conn.cursor(prepared=True)

        ts = int(time.time())

        cursor.execute(('INSERT INTO bet_votes(bet_id, user, ts, choice_id) '
                        'VALUES (%s, %s, %s, %s) '
                        'ON DUPLICATE KEY UPDATE ts = %s, choice_id = %s'),
                       (bet_id, user_id, ts, choice_id, ts, choice_id))

        cursor.execute(('INSERT INTO bet_votes_history(bet_id, user, ts, choice_id) '
                        'VALUES (%s, %s, %s, %s) '),
                       (bet_id, user_id, ts, choice_id))
        self.conn.commit()
        cursor.close()


    def bet_resolve(self, bet_id, choice_id):
        self.ensure_connected()
        cursor = self.conn.cursor(prepared=True)

        ts = int(time.time())

        cursor.execute(('UPDATE bets '
                        'SET active = 0, correct_choice_id = %s '
                        'WHERE id = %s'),
                       (choice_id, bet_id))

        self.conn.commit()
        cursor.close()


    def get_bets(self):
        self.ensure_connected()
        cursor = self.conn.cursor(prepared=True)

        cursor.execute(('SELECT b.id, b.resolve_date, q.question, b.active, c.choice '
                        'FROM bets b '
                        'INNER JOIN bet_questions q ON b.id = q.bet_id '
                        'LEFT JOIN bet_choices c '
                        'ON c.id = b.correct_choice_id AND c.bet_id = b.id '
                        'ORDER BY b.ts DESC'))

        results = cursor.fetchall()

        self.conn.commit()
        cursor.close()

        return results


    def get_bets_for_user(self, user):
        self.ensure_connected()
        cursor = self.conn.cursor(prepared=True)

        inner_query = ('SELECT b.*, c.choice AS correct_choice FROM bets b '
                       'LEFT JOIN bet_choices c '
                       'ON c.id = b.correct_choice_id AND c.bet_id = b.id')

        cursor.execute(('SELECT b.id, b.resolve_date, b.active, q.question, b.correct_choice, c.choice '
                        'FROM bet_votes v '
                        'INNER JOIN ({}) b ON b.id = v.bet_id '
                        'INNER JOIN bet_questions q ON q.bet_id = v.bet_id '
                        'INNER JOIN bet_choices c ON c.bet_id = v.bet_id AND c.id = v.choice_id '
                        'WHERE v.user = %s ').format(inner_query),
                       (user,))

        results = cursor.fetchall()

        self.conn.commit()
        cursor.close()

        return results


    def get_winners(self, bet_id):
        self.ensure_connected()
        cursor = self.conn.cursor(prepared=True)

        cursor.execute(('SELECT v.user, v.ts, b.resolve_date FROM bet_votes v '
                        'INNER JOIN bets b ON b.id = v.bet_id '
                        'AND b.correct_choice_id = v.choice_id '
                        'WHERE b.id = %s'),
                       (bet_id,))

        results = list(cursor.fetchall())

        self.conn.commit()
        cursor.close()

        return results


    def get_all_user_ids(self):
        self.ensure_connected()
        cursor = self.conn.cursor()

        cursor.execute('SELECT DISTINCT user FROM bet_votes')
        user_ids = list(cursor.fetchall())

        self.conn.commit()
        cursor.close()

        return [x[0] for x in user_ids]


    def get_user_info(self, user_id):
        self.ensure_connected()
        cursor = self.conn.cursor(prepared=True)

        cursor.execute(('SELECT name, avatar_url FROM users '
                        'WHERE id = %s'),
                       (user_id,))
        results = list(cursor.fetchall())

        self.conn.commit()
        cursor.close()

        if len(results) == 0:
            return None
        else:
            return results[0]


    def update_user_info(self, user_id, name, avatar_url):
        self.ensure_connected()
        cursor = self.conn.cursor(prepared=True)

        cursor.execute(('INSERT INTO users '
                        'VALUES (%s, %s, %s) '
                        'ON DUPLICATE KEY UPDATE name = %s, avatar_url = %s'),
                       (user_id, name, avatar_url, name, avatar_url))

        self.conn.commit()
        cursor.close()
