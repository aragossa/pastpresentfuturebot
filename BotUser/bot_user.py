
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

    def send_notification(self):
        pass


