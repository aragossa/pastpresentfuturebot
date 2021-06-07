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

    def get_results(self):
        return db_connector.get_user_results(uid=self.uid)

    def __plot_scatter(self, x, y, result):
        if result > 10:
            size = 1000
        elif result > 5:
            size = 600
        else:
            size = 100
        plt.scatter(x, y, s=size)

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

    def prepare_results(self):
        user_results = self.get_results()

        w = 6
        h = 4
        d = 200
        plt.figure(figsize=(w, h), dpi=d)
        plt.axis([-10, 10, -10, 10])

        temp_counter = 0
        for elem in user_results:
            y = self.__get_y(temp_counter)
            x = self.__get_x(temp_counter)
            self.__plot_scatter(x=x, y=y, result=int(elem))
            temp_counter += 1

        file_name = f"temp/{str(uuid.uuid4())}.png"
        log.info(f"Prepared filename {file_name}")
        plt.savefig(file_name)
        log.info("File saved")
        return file_name



