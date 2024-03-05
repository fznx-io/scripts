import json
import random
import sys
import requests
import os

os.system("trivy config /home/tabs/gcp-deployment/platform-engineering/npe/STAGE > trivy-stage-output")

stream = os.popen("sed -n '1,100p' trivy-stage-output ")
output = stream.read()
output

stream2 = os.popen("sed -n '101,200p' trivy-stage-output ")
output2 = stream2.read()
output2

def slack_notification_content(messages):
     slack_data = {
         "username": "Trivy Staging Scan Result",
         "channel": "#ts-trivy-scan",
         "text":messages
     }
     return slack_data
