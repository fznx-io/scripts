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

    pass
