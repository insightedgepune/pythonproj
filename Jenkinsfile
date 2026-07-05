pipeline {

    agent { label 'jenkins-agent-2' }

    environment {
        DEPLOY_HOST = "192.168.1.18"
        DEPLOY_USER = "vboxuser"
        DEPLOY_PATH = "/home/vboxuser/pythonproj"
        IMAGE_NAME = "python-login-app"
        CONTAINER_NAME = "python-login-container"
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    credentialsId: 'python-newproj',
                    url: 'https://github.com/insightedgepune/pythonproj.git'
            }
        }

        stage('Deploy to Target') {
            steps {

                sshagent(['target-server']) {

                    sh """
                    ssh -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_HOST} "
                    mkdir -p ${DEPLOY_PATH}
                    "
                    """

                    sh """
                    rsync -av --delete --exclude='.git' ./ \
                    ${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_PATH}/
                    """

                    sh """
                    ssh ${DEPLOY_USER}@${DEPLOY_HOST} "

                    cd ${DEPLOY_PATH}

                    docker stop ${CONTAINER_NAME} || true

                    docker rm ${CONTAINER_NAME} || true

                    docker rmi ${IMAGE_NAME} || true

                    docker build -t ${IMAGE_NAME} .

                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p 5000:5000 \
                        ${IMAGE_NAME}

                    docker ps

                    "
                    """
                }
            }
        }
    }

    post {
        success {
            echo 'Application deployed successfully.'
        }

        failure {
            echo 'Deployment failed.'
        }
    }
}
