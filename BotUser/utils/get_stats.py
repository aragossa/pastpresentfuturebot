import datetime
import operator

from utils.db_connector import bot_installs, get_avg_uses, get_blocked_users, get_yesterday_users, get_usage_density, \
    get_avg_days_block, get_avg_days_usage, get_top_refers
from utils.logger import get_logger

log = get_logger("get_stats")

class UserStats():
    def get_stats(self):
        users_count, first_install_date, last_install_date = bot_installs()
        days_uses = get_avg_uses()
        avg_days_uses = round(int(days_uses) / int(users_count), 2)
        usage_density_percent = self.get_usage_density()
        get_avg_days_block = self.get_avg_days_block()
        one_week_users, two_week_users = self.get_avg_days_usage()
        message = f"""Всего скачиваний: {users_count} 
Дата первой установки: {first_install_date}
Дата последней установки: {last_install_date}
Среднее количество дней использования бота: {avg_days_uses}
Средняя плотность использования: {usage_density_percent}%
Среднее количество дней до блокировки: {get_avg_days_block}
Количество пользователей больше недели: {len(one_week_users)}
Количество пользователей больше 2х недель: {len(two_week_users)}"""

        return message

    def get_blocked_users(self):
        blocked_users_list = get_blocked_users()
        message = "Пользователи, заблокировавшие бота:\n"
        counter = 1
        for user in blocked_users_list:
            message += f"{counter}. {user[0]}, {user[1]}, {user[2]}, {user[3]} {user[4]}\n"
            counter += 1
        return message

    def get_yestarday_users(self):
        yesterday_users_list = get_yesterday_users()
        message = "Пользователи, пользовавшиеся вчера:\n"
        counter = 1
        for user in yesterday_users_list:
            message += f"{counter}. {user[0]}, {user[1]}, {user[2]}, {user[3]}\n"
            counter += 1
        return message

    def get_usage_density(self):
        usage_density = get_usage_density()
        usage_percents = []
        for user_usage in usage_density:
            min = datetime.datetime.strptime(user_usage.get('user_data')[2], '%Y-%m-%d %H:%M:%S')
            max = datetime.datetime.strptime(user_usage.get('user_data')[1], '%Y-%m-%d %H:%M:%S')
            notification_count = user_usage.get('user_data')[0]
            results_count = user_usage.get('results_count')
            delta = max - min
            if delta.days == 0 or notification_count == 0:
                usage_percents.append(0)
            else:
                result = results_count/(delta.days * notification_count)
                usage_percents.append(result)
        usage_density_percent = sum(usage_percents)/len(usage_percents)
        return round(usage_density_percent, 3) * 100

    def get_avg_days_block(self):
        users_data = get_avg_days_block()
        days_sum = 0
        for current_user_data in users_data:
            join_date = datetime.datetime.strptime(current_user_data.get('join_date'), '%Y-%m-%d %H:%M:%S')
            block_date = datetime.datetime.strptime(current_user_data.get('block_date'), '%Y-%m-%d %H:%M:%S')
            delta = block_date - join_date
            days_sum += delta.days
        return int(days_sum/len(users_data))

    def __update_user_list(self, uid, user_list):
        if uid not in user_list:
            user_list.append(uid)
        return user_list

    def get_avg_days_usage(self):
        users_data = get_avg_days_usage()
        one_week_users = []
        two_week_users = []
        for current_user_data in users_data:
            prev_date = None
            days_counter = 0
            for elem in current_user_data.get('usage_data'):
                if prev_date:
                    current_date = datetime.datetime.strptime(elem[0], '%Y-%m-%d')
                    delta = current_date - prev_date
                    if delta.days == 1:
                        days_counter += 1
                        if days_counter >= 7:
                            self.__update_user_list(uid=current_user_data.get('uid'), user_list=one_week_users)
                        if days_counter >= 14:
                            self.__update_user_list(uid=current_user_data.get('uid'), user_list=two_week_users)
                    else:
                        days_counter = 0
                    prev_date = datetime.datetime.strptime(elem[0], '%Y-%m-%d')
                else:
                    prev_date = datetime.datetime.strptime(elem[0], '%Y-%m-%d')

        return one_week_users, two_week_users

    def top_refers(self):
        refer_list, result = get_top_refers()
        user_list = []
        for elem in result:
            user_list.append(elem[0])
        stats = {}
        min_user = None
        min_count = 0
        for user in refer_list:
            cur_min_user = user[0]
            cur_min_count = user_list.count(cur_min_user)
            if len(stats) >= 9:
                if cur_min_count > min_count:
                    stats[cur_min_user] = cur_min_count
                    if min_user:
                        stats.pop(min_user)
                    min_user = cur_min_user
                    min_count = cur_min_count
            else:
                stats[cur_min_user] = cur_min_count
        message = "Топ 10 рефералов:\n"
        c = 1
        sorted_stats = dict(sorted(stats.items(), key=operator.itemgetter(1), reverse=True))
        for uid, counts in sorted_stats.items():
            message += f"{c}. {uid} - {counts}\n"
            c += 1
        return message
