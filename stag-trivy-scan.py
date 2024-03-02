import json
import random
import sys
import requests
import os

os.system("trivy config /home/tabs/gcp-deployment/platform-engineering/npe/STAGE > trivy-stage-output")

stream = os.popen("sed -n '1,100p' trivy-stage-output ")
output = stream.read()
output
