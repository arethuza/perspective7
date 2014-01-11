import dbgateway
import random
import string
import datetime
import time

alphabet = string.ascii_letters + string.digits


def generate_token_value(length):
    sr = random.SystemRandom()
    return "".join([sr.choice(alphabet) for i in range(length)])

def in_future(days=0, hours=0, minutes=0, seconds=0):
    d = datetime.datetime.fromtimestamp(int(time.time()))
    return d + datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

class TokenManager():

    def __init__(self, locator):
        self.locator = locator

    def create_token(self, item_id, length, **kwargs):
        token_value = generate_token_value(length)
        expires_at = in_future(**kwargs).isoformat()
        dbgw = dbgateway.DbGateway(self.locator)
        dbgw.create_token(item_id, token_value, expires_at)
        return token_value, expires_at

    def find_token(self, item_id, token_value):
        dbgw = dbgateway.DbGateway(self.locator)
        return dbgw.find_token(item_id, token_value)




