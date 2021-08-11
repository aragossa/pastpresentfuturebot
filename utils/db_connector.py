import datetime
import sqlite3
import uuid

from utils.logger import get_logger

log = get_logger("db_connector")


def connection():
    connect = sqlite3.connect('data/database.db')
    cursor = connect.cursor()
    return connect, cursor


def get_api_token():
    con, cur = connection()
    with con:
        cur.execute("""SELECT value FROM configuration WHERE name = 'api_token'""")
        return cur.fetchone()[0]


def get_bot_name():
    con, cur = connection()
    with con:
        cur.execute("""SELECT value FROM configuration WHERE name = 'bot_name'""")
        return cur.fetchone()[0]


def get_delay_hours():
    con, cur = connection()
    with con:
        cur.execute("""SELECT value FROM configuration WHERE name = 'delay_hours'""")
        return cur.fetchone()[0]


def get_message_text_by_id(message_id):
    con, cur = connection()
    with con:
        cur.execute(f"""SELECT message_text FROM messages WHERE id = '{message_id}'""")
        return cur.fetchone()[0]


def get_notification_count_by_uid(uid):
    con, cur = connection()
    with con:
        cur.execute(f"""SELECT notification_count FROM users WHERE id = '{uid}'""")
        return cur.fetchone()[0]


def get_user_results(uid, start_date):
    con, cur = connection()
    with con:
        query = f"""SELECT
                        COUNT(CASE WHEN "past_m" > 0 THEN 1 END) as past_m,
                        COUNT(CASE WHEN "past_p" > 0 THEN 1 END) as past_p,
                        COUNT(CASE WHEN "past_e" > 0 THEN 1 END) as past_e,
                        COUNT(CASE WHEN "pres_m" > 0 THEN 1 END) as pres_m,
                        COUNT(CASE WHEN "pres_p" > 0 THEN 1 END) as pres_p,
                        COUNT(CASE WHEN "pres_e" > 0 THEN 1 END) as pres_e,
                        COUNT(CASE WHEN "fut_m" > 0 THEN 1 END) as fut_m,
                        COUNT(CASE WHEN "fut_p" > 0 THEN 1 END) as fut_p,
                        COUNT(CASE WHEN "fut_e" > 0 THEN 1 END) as fut_e
                  FROM results
                  WHERE
                    ("creation_date" >= "{start_date}")
                  AND
                    (id = {uid})
                """
        # log.info(query)

        """Comment"""
        cur.execute(query)
        return cur.fetchall()[0]


def get_start_results_date(uid):
    con, cur = connection()
    with con:
        query = f"""SELECT min(creation_date) FROM results
                    WHERE id = {uid}"""
        cur.execute(query)
        return cur.fetchone()[0]


def get_user_results_between(uid, start_date, fin_date):
    con, cur = connection()
    with con:
        query = f"""SELECT
                        COUNT(CASE WHEN "past_m" > 0 THEN 1 END) as past_m,
                        COUNT(CASE WHEN "past_p" > 0 THEN 1 END) as past_p,
                        COUNT(CASE WHEN "past_e" > 0 THEN 1 END) as past_e,
                        COUNT(CASE WHEN "pres_m" > 0 THEN 1 END) as pres_m,
                        COUNT(CASE WHEN "pres_p" > 0 THEN 1 END) as pres_p,
                        COUNT(CASE WHEN "pres_e" > 0 THEN 1 END) as pres_e,
                        COUNT(CASE WHEN "fut_m" > 0 THEN 1 END) as fut_m,
                        COUNT(CASE WHEN "fut_p" > 0 THEN 1 END) as fut_p,
                        COUNT(CASE WHEN "fut_e" > 0 THEN 1 END) as fut_e
                  FROM results
                  WHERE
                    ("creation_date" >= "{start_date}")
                  AND
                    ("creation_date" < "{fin_date}")
                  AND
                    (id = {uid})
                """
        # log.info(query)

        """Comment"""
        cur.execute(query)
        return cur.fetchall()[0]


def check_auth(uid):
    con, cur = connection()
    with con:
        cur.execute(f"SELECT id FROM users WHERE id = {uid}")
        return cur.fetchone()


def add_user(uid, refer_id):
    con, cur = connection()

    with con:
        cur.execute(f"""INSERT INTO users (id) VALUES ({uid})""")
        if refer_id is not None:
            log.info("found refer_id")
            cur.execute(f"""INSERT INTO users_state (id, refer_id) VALUES ({uid}, {refer_id})""")
        else:
            log.info("not found refer_id")
            cur.execute(f"""INSERT INTO users_state (id) VALUES ({uid})""")
        return True


def get_user_state(uid):
    con, cur = connection()
    with con:
        cur.execute(f"""SELECT state, input_value FROM users_state WHERE id ={uid}""")
        return cur.fetchone()


def select_last_notification(uid):
    con, cur = connection()
    with con:
        cur.execute(f"""SELECT * FROM scheduled 
                        WHERE id = (SELECT MAX(id) FROM scheduled WHERE uid ={uid})
        """)
        return cur.fetchone()


def update_user_state(uid, state, input_value):
    con, cur = connection()
    with con:
        cur.execute(f"""UPDATE users_state SET state = '{state}', input_value = '{input_value}' WHERE id ={uid}""")
        return cur.fetchone()


def update_notification_count(uid, data):
    con, cur = connection()
    with con:
        cur.execute(f"""UPDATE users SET notification_count = {data} WHERE id = {uid} """)
        return True


def increment_answers(user, data, creation_date):
    con, cur = connection()
    with con:
        query = f"""INSERT INTO results  ("id", "{data}", "creation_date") VALUES ({user.uid}, 1, '{creation_date}')"""
        log.info(query)
        cur.execute(query)
        return True


def get_notifications():
    con, cur = connection()
    with con:
        datetime_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(f"""SELECT id, message_type, uid, scheduled_time, status, step_id, message_id FROM scheduled
                        WHERE scheduled_time <= '{datetime_now}'
                        AND status = 'NEW'""")
        return cur.fetchall()

def get_last_notification_status(uid):
    con, cur = connection()
    with con:
        query = f"""SELECT status, message_id FROM scheduled
                    WHERE id = (SELECT MAX(id) from scheduled 
                                WHERE uid = {uid}
                                AND message_id is not NULL)"""
        log.debug(query)
        cur.execute(query)
        return cur.fetchone()



def set_notification_sent(notification_id):
    con, cur = connection()
    with con:
        cur.execute(f"""UPDATE scheduled SET status = 'SENT' WHERE id = {notification_id} """)
        return True

def set_notification_complite(notification_id):
    con, cur = connection()
    with con:
        cur.execute(f"""UPDATE scheduled SET status = 'COMPLITE'
                        WHERE id = {notification_id}""")
        return True

def update_message_id(notification_id, message_id):
    con, cur = connection()
    with con:
        cur.execute(f"""UPDATE scheduled SET message_id = {message_id} WHERE id = {notification_id} """)
        return True


def add_notification(current, next_datetime, step_id):
    con, cur = connection()
    with con:
        query = f"""INSERT INTO scheduled (message_type, uid, scheduled_time, step_id)
                        VALUES ('{current.type}', {current.uid}, '{next_datetime}', {step_id})"""
        log.info(query)
        cur.execute(query)
        return True


def get_max_notification_id():
    con, cur = connection()
    with con:
        cur.execute("SELECT MAX(id) FROM scheduled")
        return int(cur.fetchone()[0]) + 1


