import json
import random
import sys
import requests
import os
from secrets import SLACK_WEBHOOK_URL
stream = os.popen('GOOGLE_APPLICATION_CREDENTIALS={GOOGLE_APPLICATION_CREDENTIALS} CLOUDSDK_CORE_PROJECT={GCP_PROJECT_NPE_NETWORK} driftctl scan --quiet  --to gcp+tf --from tfstate+gs://ts-cloudstorage-npe-terraform/terraform/npe/host/default.tfstate')
output = stream.read()
output

def slack_notification_content():
     slack_data = {
         "username": "NPE NETWORK Driftctl Scan Result",
         "channel": "#ts-driftctl-notifications",
         "text":output
     }
     return slack_data
def slack_webhook(webhook_url):
    slack_data = slack_notification_content()
    headers = {
        'Content-Type': "application/json",
    }
    response = requests.post(
        webhook_url,
        data=json.dumps(slack_data),
        headers=headers
    )
    if response.status_code == 200:
        print("Scan result sucessfully sent")
if __name__ == '__main__':
    webhook_url = SLACK_WEBHOOK_URL
    slack_webhook(webhook_url)
