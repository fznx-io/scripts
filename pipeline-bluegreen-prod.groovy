repo_name = 'REPOSITORY_NAME'                  // change this
repo_url = repo_project + repo_name
repo_branch = 'BRANCH_NAME'                // change this
service_name = 'SERVICE_NAME'                   // change this
env = 'prod'

pipeline {
    agent any

    stages {
        stage("Fetching The Code & Config") {
            steps {
                script {
                    if( user != "" ){
                        slackSend(channel: "ts-build-production-notifications", message:"*$user*'s build on pipeline *$service_name* on branch *$repo_branch* of repo *$repo_name* is *started*")
                    }
                }
                git url: repo_url, credentialsId: repo_key, branch: repo_branch

                sh "cp -r $appconfig_prod/$service_name-$env/* ."
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
                sh "docker build -t $imagerepo_prod/$service_name:$env.$build_number ."
                sh "docker tag $imagerepo_prod/$service_name:$env.$build_number $imagerepo_prod/$service_name:$env.$latest"
            }
        }

        stage("Pushing to The Registry") {
            steps {
                sh "docker push $imagerepo_prod/$service_name:$env.$build_number"
                sh "docker push $imagerepo_prod/$service_name:$env.$latest"
            }
        }

        stage("Deploying to The Cluster") {
            steps {
                script {
                    def state = sh(
                              script: '''kubectl get virtualservice ''' + service_name + ''' -o jsonpath="{..host}" --kubeconfig=$kubeconfig_prod''',
                              returnStdout: true) 
                    if ("$state" =~ "blue" ){
                        old_state = "blue"
                        new_state = "green"
                    }else{
                        old_state = "green"
                        new_state = "blue"
                    }
                    println "deploying to $service_name $new_state ..."
                    sh "kubectl set image deployment/$service_name-$new_state $service_name-$new_state=$imagerepo_prod/$service_name:$env.$build_number --kubeconfig=$kubeconfig_prod"
                    sh "kubectl scale deployment/$service_name-$new_state --replicas=1 --kubeconfig=$kubeconfig_prod"
                    sh "sleep 2m"
                    timeout(time:1, unit: 'HOURS') {
                        input(message: "Steer traffic to $new_state deployment now?")
                    }
                    sh "kubectl patch virtualservice $service_name --type=merge -p '{\"spec\":{\"http\": [{\"route\": [{\"destination\": {\"host\": \"$service_name-$new_state\" }}] }] }}' --kubeconfig=$kubeconfig_prod"
                    sh "kubectl scale deployment/$service_name-$old_state --replicas=0 --kubeconfig=$kubeconfig_prod"
                    println "Traffic has been steered to $new_state deployment"
                    
                    //Deploying to sw-domain-prefix namespace
                    // sh "kubectl set image -n sw-domain-prefix deployment/$service_name $service_name=$imagerepo_prod/$service_name:$env.$build_number --kubeconfig=$kubeconfig_prod"
                }    
            }
        }
    }
    post{
        success{
            script {
                if( user != "" ){
                    slackSend(color:"good", channel: "ts-build-production-notifications", message:"*$user*'s build on pipeline *$service_name* on branch *$repo_branch* of repo *$repo_name* is *deployed* \n ```$commit_message```")
                }
            }
        }
        failure{
            script {
                if( user != "" ){
                    slackSend(color:"danger", channel: "ts-build-production-notifications", message:"*$user*'s build on pipeline *$service_name* on branch *$repo_branch* of repo *$repo_name* is *failed*")
                }
            }
        }
    }
}