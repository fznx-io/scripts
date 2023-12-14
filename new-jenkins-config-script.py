import os
import subprocess
from secrets import JENKINS_BASE_PATH

def jenkins_updater(folder, action):
    base_path = JENKINS_BASE_PATH
    list_pipelines = [f.name for f in os.scandir(os.path.join(base_path, folder, "jobs")) if f.is_dir()]

    print(list_pipelines)

if __name__ == "__main__":
    env = input("Environment? ")
    action = input("Action (new/edit)? ").lower()

    if action not in ["new", "edit"]:
        print("Invalid action. Use 'new' or 'edit'.")
    else:
        jenkins_updater(env, action)
