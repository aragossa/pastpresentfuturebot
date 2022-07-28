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

def get_notification_scheduled_time(notification_id):
    con, cur = connection()
    with con:
        cur.execute(f"""SELECT scheduled_time FROM scheduled WHERE id = '{notification_id}'""")
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


def add_user(uid, username, first_name, last_name, refer_id):
    con, cur = connection()

    with con:
        cur.execute(f"""INSERT INTO users (id, username, first_name, last_name)
                        VALUES ({uid}, '{username}', '{first_name}', '{last_name}')""")
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


def increment_answers(user, data, creation_date, response_time=0):
    con, cur = connection()
    with con:
        query = f"""INSERT INTO results  ("id", "{data}", "creation_date", "response_time") VALUES ({user.uid}, 1, '{creation_date}', {response_time})"""
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


def set_notification_blocked(notification_id):
    con, cur = connection()
    with con:
        cur.execute(f"""UPDATE scheduled SET status = 'BLOCKED'
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
        query = f"""INSERT INTO scheduled (message_type, uid, scheduled_time, step_id, status)
                        VALUES ('{current.type}', {current.uid}, '{next_datetime}', {step_id}, 'NEW')"""
        log.info(query)
        cur.execute(query)
        return True


def get_max_notification_id():
    con, cur = connection()
    with con:
        cur.execute("SELECT MAX(id) FROM scheduled")
        return int(cur.fetchone()[0]) + 1


def get_bot_active_users():
    con, cur = connection()
    with con:
        cur.execute("SELECT uid FROM scheduled WHERE status = 'NEW'")
        return cur.fetchall()


def get_bot_users():
    con, cur = connection()
    with con:
        cur.execute("SELECT id, username, first_name, last_name, joined_at FROM users")
        return cur.fetchall()


""" Users stats """


def bot_installs():
    con, cur = connection()
    with con:
        cur.execute("select max(joined_at) from users")
        last_install_date = cur.fetchone()[0]
        cur.execute("select min(joined_at) from users")
        first_install_date = cur.fetchone()[0]
        cur.execute("select count(*) from users")
        users_count = cur.fetchone()[0]
        return users_count, first_install_date, last_install_date


def get_avg_uses():
    con, cur = connection()
    with con:
        cur.execute("SELECT COUNT(DISTINCT DATE(creation_date)) FROM results")
        return cur.fetchone()[0]


def get_blocked_users():
    con, cur = connection()
    with con:
        cur.execute("""select distinct u.id, u.username, u.first_name, u.last_name, s.scheduled_time
                       from scheduled s
                       left join users u on u.id = s.uid
                       where s.status = 'BLOCKED'
                       order by s.scheduled_time desc
                       limit 30 """)
        return cur.fetchall()


def get_yesterday_users():
    con, cur = connection()
    with con:
        cur.execute("""select distinct u.id, u.username, u.first_name, u.last_name
                       from results r
                       left join users u on u.id = r.id
                       where DATE(creation_date) = DATE('now', '-1 day')""")
        return cur.fetchall()


def get_usage_density():
    con, cur = connection()
    with con:
        cur.execute("select id from users")
        user_list = cur.fetchall()
    user_data = []
    for user in user_list:
        cur.execute(f"select count(*) from results where id = {user[0]}")
        results_count = cur.fetchone()[0]
        cur.execute(f"""select  u.notification_count as notification_count,
                                max(s.scheduled_time) as max,
                                min(s.scheduled_time) as min,
                                u.id as uid
                       from users u
                       left join scheduled s on s.uid = u.id
                       where u.id = {user[0]}""")

        user_data.append({'results_count': results_count, 'user_data': cur.fetchone()})
    return user_data


def get_avg_days_block():
    con, cur = connection()
    users_data = []
    with con:
        cur.execute("select uid, scheduled_time from scheduled where status = 'BLOCKED'")
        query_result = cur.fetchall()
        for user_data in query_result:
            cur.execute(f"select joined_at from users where id = {user_data[0]}")
            join_date = cur.fetchone()[0]
            users_data.append({'uid': user_data[0], 'block_date': user_data[1], 'join_date': join_date})
    return users_data


def get_avg_days_usage():
    con, cur = connection()
    users_data = []
    with con:
        cur.execute("select id from users")
        user_list = cur.fetchall()

        for user in user_list:
            cur.execute(f"""select distinct date(scheduled_time) from scheduled
                            where status = 'COMPLITE' and uid = {user[0]}
                            order by scheduled_time""")
            user_usage = cur.fetchall()
            users_data.append({'uid': user[0], 'usage_data': user_usage})
    return users_data

def get_avg_reponse():
    con, cur = connection()
    with con:
        cur.execute("""select avg(response_time)
            from results
            where response_time <> 0;""")
        return cur.fetchone()[0]

def get_top_refers():
    con, cur = connection()
    with con:
        cur.execute("""select refer_id from users_state
                        where refer_id is not null
                        group by refer_id""")
        refer_list = cur.fetchall()

        cur.execute(f"""select refer_id from users_state
                        where refer_id is not null""")
        result = cur.fetchall()
    return refer_list, result


def check_refer_id(uid):
    con, cur = connection()
    with con:
        cur.execute(f"""select id from users
                        where id = '{uid}'""")
        result = cur.fetchall()
    if len(result) > 0:
        return True
    else:
        return False


def get_feedbacks():
    con, cur = connection()
    with con:
        cur.execute(f"""select count(*) from scheduled where message_type = 'FEEDBACK' and status = 'SENT'""")
        return cur.fetchone()