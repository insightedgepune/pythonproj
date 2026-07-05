pipeline {

    agent { label 'jenkins-agent-2' }

    environment {
        DEPLOY_HOST    = "192.168.1.18"
        DEPLOY_USER    = "vboxuser"
        DEPLOY_PATH    = "/home/vboxuser/pythonproj"
        IMAGE_NAME     = "python-login-app"
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

                sshagent(credentials: ['target-server']) {

                    // Create deployment directory
                    sh """
                    ssh -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_HOST} \
                    "mkdir -p ${DEPLOY_PATH}"
                    """

                    // Copy project files
                    sh """
                    rsync -av --delete \
                    --exclude='.git' \
                    ./ ${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_PATH}/
                    """

                    // Build and run container
                    sh """
                    ssh -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_HOST} '
                        set -e

                        cd ${DEPLOY_PATH}

                        echo "Stopping old container..."
                        docker stop ${CONTAINER_NAME} || true

                        echo "Removing old container..."
                        docker rm ${CONTAINER_NAME} || true

                        echo "Removing old image..."
                        docker rmi ${IMAGE_NAME} || true

                        echo "Building Docker image..."
                        docker build -t ${IMAGE_NAME} .

                        echo "Starting new container..."
                        docker run -d \
                            --name ${CONTAINER_NAME} \
                            -p 5000:5000 \
                            ${IMAGE_NAME}

                        echo "Running containers:"
                        docker ps
                    '
                    """
                }
            }
        }
    }

    post {

        success {
            echo "Application deployed successfully."
        }

        failure {
            echo "Deployment failed."
        }

        always {
            cleanWs()
        }
    }
}
