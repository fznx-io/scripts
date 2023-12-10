import os
import subprocess

def jenkins_updater(folder, action):
    # TODO: Implement Jenkins updater
    pass

if __name__ == "__main__":
    env = input("Environment? ")
    action = input("Action (new/edit)? ").lower()

    if action not in ["new", "edit"]:
        print("Invalid action. Use 'new' or 'edit'.")
    else:
        jenkins_updater(env, action)
