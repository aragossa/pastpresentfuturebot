import datetime
import os
import time
import imageio
import matplotlib.pyplot as plt
import uuid

import utils.db_connector
from utils import db_connector
from utils.logger import get_logger

log = get_logger("bot_user")


class Botuser:

    def __init__(self, uid):
        self.uid = uid

    @staticmethod
    def get_last_notification_status(uid):
        query_result = db_connector.get_last_notification_status(uid)
        log.info(query_result)
        if query_result is not None:
            status = query_result[0]
            message_id = query_result[1]
        else:
            status = None
            message_id = None
        return status, message_id

    def check_auth(self):
        if utils.db_connector.check_auth(self.uid):
            return True
        else:
            return False

    def add_user(self, refer_id=None):
        db_connector.add_user(uid=self.uid, refer_id=refer_id)

    def get_results(self, start_date):
        return db_connector.get_user_results(uid=self.uid, start_date=start_date)

    def get_results_between(self, start_date, fin_date):
        return db_connector.get_user_results_between(uid=self.uid, start_date=start_date, fin_date=fin_date)

    def __plot_scatter(self, x, y, result, result_sum):
        if result > 15:
            size = 1500
        elif result > 10:
            size = 1000
        elif result > 5:
            size = 600
        elif result == 0:
            size = 0
        else:
            size = 100
        plt.scatter(x, y, s=size)
        if result > 0:
            plt.text(x + .5, y, f"{result} ({round(result / result_sum * 100, 2)}%)")

    def __get_y(self, counter):
        if counter % 3 == 0:
            return -5
        elif counter % 3 == 1:
            return +5
        elif counter % 3 == 2:
            return 0

    def __get_x(self, counter):
        if counter // 3 == 0:
            return -5
        elif counter // 3 == 1:
            return 0
        elif counter // 3 == 2:
            return 5

    def get_last_notification(self):
        return utils.db_connector.select_last_notification(self.uid)

    def plot_figure(self):
        w = 6
        h = 4
        d = 100
        fig = plt.figure(figsize=(w, h), dpi=d)
        return fig

    def add_axes(self, fig):
        ax = fig.add_subplot(1, 1, 1)
        # ax.xlim(-10, 10)
        ax.set_xlim(left=-7, right=7)
        ax.set_ylim(bottom=-7, top=7)
        ax.text(-6, 8, "Прошлое")
        ax.text(-1, 8, "Настоящее")
        ax.text(4, 8, "Будущее")

        # Move left y-axis and bottim x-axis to centre, passing through (0,0)
        ax.spines['left'].set_position('center')
        ax.spines['bottom'].set_position('center')

        # Eliminate upper and right axes
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')

        # Turn off tick labels
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        return fig

    def add_result_to_fig(self, user_results):
        temp_counter = 0
        result_sum = 0
        for i in user_results:
            result_sum += int(i)

        for elem in user_results:
            y = self.__get_y(temp_counter)
            x = self.__get_x(temp_counter)
            self.__plot_scatter(x=x, y=y, result=int(elem), result_sum=result_sum)
            temp_counter += 1

    def prepare_results(self):
        start_date = datetime.datetime.now() - datetime.timedelta(days=30)
        log.info(start_date.strftime('%d.%m.%y %H:%M:%S'))
        user_results = self.get_results(start_date=start_date.strftime('%Y-%m-%d %H:%M:%S'))
        print(user_results)
        fig = self.plot_figure()
        self.add_axes(fig=fig)
        self.add_result_to_fig(user_results=user_results)

        file_name = f"temp/{str(uuid.uuid4())}.png"
        log.info(f"Prepared filename {file_name}")
        plt.savefig(file_name)
        log.info("File saved")
        return file_name

    def prepare_results_dyn(self):
        start_date = db_connector.get_start_results_date(self.uid)
        formatted_start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        log.info(start_date)

        file_names = []
        fin_date = formatted_start_date + datetime.timedelta(days=7)
        prev_results = ""
        user_week_result = None
        log.info(prev_results == user_week_result)
        while True:
            log.info(f"prev_results {prev_results}")
            log.info(f"user_week_result {user_week_result}")
            log.info(prev_results == user_week_result)
            log.info(f"formatted_start_date {formatted_start_date}")
            log.info(f"fin_date {fin_date}")
            fig = self.plot_figure()
            self.add_axes(fig=fig)

            user_week_result = self.get_results_between(start_date=formatted_start_date, fin_date=fin_date)
            self.add_result_to_fig(user_results=user_week_result)
            file_name = f"temp/{str(uuid.uuid4())}.png"
            log.info(f"Prepared filename {file_name}")
            plt.savefig(file_name)
            file_names.append(file_name)
            log.info("File saved")


            log.info("---------------------------")
            log.info(f"prev_results {prev_results}")
            log.info(f"user_week_result {user_week_result}")
            log.info(prev_results == user_week_result)
            if prev_results == user_week_result:
                log.info("break")
                break
            else:
                log.info("continue")
                prev_results = user_week_result
                fin_date = fin_date + datetime.timedelta(days=7)

        images = []
        for cur_file_name in file_names:
            images.append(imageio.imread(f"{cur_file_name}"))
        gif_file_name = f'temp/{str(uuid.uuid4())}.gif'
        imageio.mimsave(gif_file_name, images, duration=1)
        return gif_file_name, file_names

    def set_notification_complite(self, notification_id):
        db_connector.set_notification_complite(notification_id)

    def get_bot_active_users(self):
        query_result = db_connector.get_bot_active_users()
        users = []
        for curr_result in query_result:
            users.append(curr_result[0])
        log.info(users)
        return users