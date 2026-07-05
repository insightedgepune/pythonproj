pipeline {

    agent { label 'jenkins-agent-2' }

    environment {
        DEPLOY_HOST = '192.168.1.18'
        DEPLOY_USER = 'vboxuser'
        DEPLOY_PATH = '/home/vboxuser/flask-login'
    }

    stages {

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t flask-login:latest .
                '''
            }
        }

        stage('Deploy') {
            steps {

                sshagent(credentials: ['target-server']) {

                    sh '''
                    ssh -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_HOST} \
                    "mkdir -p ${DEPLOY_PATH}"
                    '''

                    sh '''
                    rsync -avz --delete ./ \
                    ${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_PATH}/
                    '''

                    sh '''
                    ssh ${DEPLOY_USER}@${DEPLOY_HOST} "
                        cd ${DEPLOY_PATH}
                        docker compose down || true
                        docker compose up -d --build
                    "
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Deployment Successful'
        }

        failure {
            echo 'Deployment Failed'
        }
    }
}
