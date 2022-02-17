repo_name = 'REPOSITORY_NAME'                  // change this
repo_url = repo_project + repo_name
repo_branch = 'BRANCH_NAME'                // change this
service_name = 'SERVICE_NAME'                   // change this
env = 'uat'

pipeline {
    agent any

    stages {
        stage("Fetching The Code & Config") {
            steps {
                script {
                    if( user != "" ){
                        slackSend(channel: "ts-build-npe-notifications", message:"*$user*'s build on pipeline *$service_name* on branch *$repo_branch* of repo *$repo_name* is *started*")
                    }
                }
                git url: repo_url, credentialsId: repo_key, branch: repo_branch

                sh "cp -r $appconfig_uat/$service_name-$env/* ."
                sh "cp -r $appconfig_uat/$service_name-$env/resources/* src/main/resources/"
                sh "mvn clean package"
            }
        }

        stage('Versioning The Service') {
            steps {
                script {
                    load '/home/tabs/gcp-deployment/infrastructure-gcp/pipelines/app-versioning.groovy'
                }
            }
        }
		
        stage("Building The Image") {
            steps {
                sh "docker build -t $imagerepo_uat/$service_name:$env.$build_number ."
                sh "docker tag $imagerepo_uat/$service_name:$env.$build_number $imagerepo_uat/$service_name:$env.$latest"
            }
        }

        stage("Pushing to The Registry") {
            steps {
                sh "docker push $imagerepo_uat/$service_name:$env.$build_number"
                sh "docker push $imagerepo_uat/$service_name:$env.$latest"
            }
        }

        stage("Deploying to The Cluster") {
            steps {
                sh "kubectl set image deployment/$service_name $service_name=$imagerepo_uat/$service_name:$env.$build_number --kubeconfig=$kubeconfig_uat"
            }
        }
    }
    post{
        success{
            script {
                if( user != "" ){
                    slackSend(color:"good", channel: "ts-build-npe-notifications", message:"*$user*'s build on pipeline *$service_name* on branch *$repo_branch* of repo *$repo_name* is *deployed* \n ```$commit_message```")
                }
            }
        }
        failure{
            script {
                if( user != "" ){
                    slackSend(color:"danger", channel: "ts-build-npe-notifications", message:"*$user*'s build on pipeline *$service_name* on branch *$repo_branch* of repo *$repo_name* is *failed*")
                }
            }
        }
    }
}