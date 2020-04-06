import os
import psycopg2
import pymongo
from jira import JIRA
from pymongo import MongoClient

def indexing():
    service = os.environ["SERVICE"]
    admin_pwd = os.environ["ADMIN_PWD"]
    database = os.environ["DATABASE"]
    collection = os.environ["COLLECTION"]
    new_index = os.environ["NEW_INDEX"]
    issue_key = os.environ["ISSUE_KEY"]
    jira_user = os.environ["ISSUE_KEY"]
    jira_token = os.environ["JIRA_TOKEN"]

    con = psycopg2.connect(database="DATABASE", user="USER", password=admin_pwd, host="HOST", port="5432")
    cur = con.cursor()
    cur.execute("SELECT ips FROM mongo_hosts WHERE service = '" + service + "'")
    ips = cur.fetchone()
    ip = ips[0]
    cur.execute("SELECT password FROM users WHERE username = 'USER'")
    pwds = cur.fetchone()
    pwd = pwds[0]

    pass
