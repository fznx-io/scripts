import json
import random
import sys
import requests
import os
from secrets import SLACK_WEBHOOK_URL, GOOGLE_APPLICATION_CREDENTIALS, GCP_PROJECT_STAGE

os.system(f"GOOGLE_APPLICATION_CREDENTIALS={GOOGLE_APPLICATION_CREDENTIALS} CLOUDSDK_CORE_PROJECT={GCP_PROJECT_STAGE} driftctl scan --quiet --to gcp+tf --from tfstate+gs://ts-cloudstorage-asiase1-npe-stage/terraform/npe/stage/default.tfstate > stage-output")

stream = os.popen("sed -n '1,100p' stage-output ")
output = stream.read()
output

stream2 = os.popen("sed -n '101,200p' stage-output ")
output2 = stream2.read()
output2

def slack_notification_content(messages):
     slack_data = {
         "username": "STAGING Driftctl Scan Result",
         "channel": "#ts-driftctl-notifications",
         "text":messages
     }
     return slack_data
def slack_webhook(webhook_url):
    slack_data = slack_notification_content(output)
    slack_data2 = slack_notification_content(output2)
    headers = {
        'Content-Type': "application/json",
    }
    response = requests.post(
        webhook_url,
        data=json.dumps(slack_data),
        headers=headers
    )
    response2 = requests.post(
        webhook_url,
        data=json.dumps(slack_data2),
        headers=headers
    )
    if response.status_code and response2.status_code == 200:
        print("Scan result sucessfully sent")

if __name__ == '__main__':
    webhook_url = SLACK_WEBHOOK_URL
    slack_webhook(webhook_url)