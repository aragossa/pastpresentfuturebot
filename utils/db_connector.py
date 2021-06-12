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

def get_user_results(uid):
    con, cur = connection()
    with con:
        cur.execute(f"""SELECT past_m, past_p, past_e, pres_m, pres_p, pres_e, fut_m, fut_p, fut_e 
                        FROM users WHERE id = '{uid}'""")
        return cur.fetchall()[0]



def check_auth(uid):
    con, cur = connection()
    with con:
        cur.execute(f"SELECT id FROM users WHERE id = {uid}")
        return cur.fetchone()


def add_user(uid):
    con, cur = connection()
    with con:
        cur.execute(f"""INSERT INTO users (id) VALUES ({uid})""")
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

def increment_answers(user, data):
    con, cur = connection()
    with con:
        cur.execute(f"""UPDATE users SET "{data}" = "{data}" + 1 WHERE id = {user.uid} """)
        return True


def get_notifications():
    con, cur = connection()
    with con:
        datetime_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(f"""SELECT * FROM scheduled WHERE scheduled_time <= '{datetime_now}' AND status = 'NEW'""")
        return cur.fetchall()


def set_notification_sent(notification_id):
    con, cur = connection()
    with con:
        cur.execute(f"""UPDATE scheduled SET status = 'SENT' WHERE id = {notification_id} """)
        return True


def add_notification(current, next_datetime, step_id):
    con, cur = connection()
    with con:
        cur.execute(f"""INSERT INTO scheduled (message_type, uid, scheduled_time, step_id)
                        VALUES ('{current.type}', {current.uid}, '{next_datetime}', {step_id})""")
        return True


def get_max_notification_id():
    con, cur = connection()
    with con:
        cur.execute("SELECT MAX(id) FROM scheduled")
        return int(cur.fetchone()[0]) + 1