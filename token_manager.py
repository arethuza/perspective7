import dbgateway
import random
import string
import datetime
import time

alphabet = string.ascii_letters + string.digits


def generate_token_value(length):
    sr = random.SystemRandom()
    return "".join([sr.choice(alphabet) for i in range(length)])

def days_in_future(days):
    d = datetime.datetime.fromtimestamp(int(time.time()))
    return d + datetime.timedelta(days=days)

class TokenManager():

    def __init__(self, locator):
        self.locator = locator

    def create_token(self, item_id, length, expiry_days):
        token_value = generate_token_value(length)
        expires_at = days_in_future(expiry_days)
        dbgw = dbgateway.DbGateway(self.locator)
        dbgw.create_token(item_id, token_value, expires_at)
        return token_value, expires_at




