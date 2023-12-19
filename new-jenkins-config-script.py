import os
import subprocess
from secrets import JENKINS_USER, JENKINS_API_TOKEN, JENKINS_URL, JENKINS_BASE_PATH

def jenkins_updater(folder, action):
    base_path = JENKINS_BASE_PATH
    list_pipelines = [f.name for f in os.scandir(os.path.join(base_path, folder, "jobs")) if f.is_dir()]

    print(list_pipelines)

    for pipeline in list_pipelines:
        pipeline_path = os.path.join(base_path, folder, "jobs", pipeline)
        os.chdir(pipeline_path)

        jenkins_url = f"{JENKINS_URL}/job/{folder}"
        jenkins_auth = f"{JENKINS_USER}:{JENKINS_API_TOKEN}"

        if action == "new":
            create_item_url = f"{jenkins_url}/createItem?name={pipeline}"
            command = ["curl", "--user", jenkins_auth, "-X", "POST", create_item_url, "-H", "Content-Type:application/xml", "--data-binary", "@config.xml"]
        elif action == "edit":
            edit_item_url = f"{jenkins_url}/job/{pipeline}/config.xml"
            command = ["curl", "--user", jenkins_auth, "-X", "POST", edit_item_url, "-H", "Content-Type:application/xml", "--data-binary", "@config.xml"]

        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error updating {pipeline}: {e}")

if __name__ == "__main__":
    env = input("Environment? ")
    action = input("Action (new/edit)? ").lower()

    if action not in ["new", "edit"]:
        print("Invalid action. Use 'new' or 'edit'.")
    else:
        jenkins_updater(env, action)
