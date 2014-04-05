import requests
import json
import datetime
import dateutil.parser

SERVICE_URL = "http://localhost:8080"
SYSTEM_USER = "system"
SYSTEM_PASSWORD = "password"


def log_in(test, path, user=SYSTEM_USER, password=SYSTEM_PASSWORD):
    url = SERVICE_URL + path
    r = requests.get(url, params={"name": user, "password": password}, verify=False)
    response = json.loads(r.content.decode("utf-8"))
    # Check response is the expected structure
    test.assertEquals(len(response), 4)
    test.assertTrue("user_path" in response)
    test.assertTrue("account_path" in response)
    test.assertTrue("token" in response)
    test.assertTrue("expires_at" in response)
    # Check that fields look OK
    check_path(test, response["user_path"])
    check_path(test, response["account_path"])
    check_in_future(test, response["expires_at"])
    token = response["token"]
    check_token(test, token)
    return token


def check_path(test, path):
    test.assertIsNotNone(path)
    test.assertTrue(len(path) >= 0)
    test.assertEquals(path[0], "/")


def check_token(test, token):
    test.assertIsNotNone(token)
    test.assertTrue(len(token) >= 40)


def check_in_future(test, time_string):
    test.assertIsNotNone(time_string)
    t = dateutil.parser.parse(time_string)
    limit = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
    test.assertTrue(t > limit)
