import datetime
import os
import time

import matplotlib.pyplot as plt
import uuid

import utils.db_connector
from utils import db_connector
from utils.logger import get_logger
log = get_logger("bot_user")


class Botuser:

    def __init__(self, uid):
        self.uid = uid

    def check_auth(self):
        if utils.db_connector.check_auth(self.uid):
            return True
        else:
            return False

    def add_user(self):
        db_connector.add_user(uid=self.uid)

    def get_results(self, start_date):
        return db_connector.get_user_results(uid=self.uid, start_date=start_date)

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
            plt.text(x+.5, y, f"{result} ({round(result/result_sum*100, 2)}%)")

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


    def prepare_results(self):
        start_date = datetime.datetime.now() - datetime.timedelta(days=30)
        log.info(start_date.strftime('%d.%m.%y %H:%M:%S'))
        user_results = self.get_results(start_date=start_date.strftime('%Y-%m-%d %H:%M:%S'))
        print(user_results)

        w = 6
        h = 4
        d = 100
        fig = plt.figure(figsize=(w, h), dpi=d)


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

        temp_counter = 0
        result_sum = 0
        for i in user_results:
            result_sum += int(i)

        for elem in user_results:
            y = self.__get_y(temp_counter)
            x = self.__get_x(temp_counter)
            self.__plot_scatter(x=x, y=y, result=int(elem), result_sum=result_sum)
            temp_counter += 1


        file_name = f"temp/{str(uuid.uuid4())}.png"
        log.info(f"Prepared filename {file_name}")
        plt.savefig(file_name)
        log.info("File saved")
        return file_name



