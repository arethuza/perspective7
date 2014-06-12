import requests
import datetime
import dateutil.parser

SERVICE_URL = "http://localhost:8080"
SYSTEM_USER = "system"
SYSTEM_PASSWORD = "password"

auth_token = None

def log_in(test, path, name=SYSTEM_USER, password=SYSTEM_PASSWORD, failure_status=None, failure_message=None):
    url = SERVICE_URL + path
    data = {}
    if name is not None:
        data["name"] = name
    if password is not None:
        data["password"] = password
    r = requests.post(url, data=data, verify=False)
    if failure_status:
        test.assertEquals(r.status_code, failure_status)
        test.assertEquals(r.text, failure_message)
        return
    response = r.json
    test.assertEquals(200, r.status_code)
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
    global auth_token
    auth_token = response["token"]
    check_token(test, auth_token)

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


def get_json(test, path, failure_status=None, failure_message=None, send_auth_header=True):
    url = SERVICE_URL + path
    r = requests.get(url, headers={"Authorization": _get_auth_header()} if send_auth_header else {})
    if failure_status:
        test.assertEquals(r.status_code, failure_status)
        test.assertEquals(r.text, failure_message)
        return
    test.assertEquals(r.status_code, 200)
    return r.json

def _get_auth_header():
        return "Bearer " + auth_token