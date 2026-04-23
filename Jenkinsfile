pipeline {
    agent { label 'worker1 || worker2' }

    parameters {
        string(name: 'BRANCH_NAME', defaultValue: 'elenak-class-work', description: 'Branch name')
        booleanParam(name: 'SKIP_DEPLOY', defaultValue: false, description: 'Skip deploy?')
    }

    stages {
        stage('Env Info') {
            steps {
                // Печать переменных по заданию
                echo "BUILD_ID: ${env.BUILD_ID}"
                echo "BUILD_URL: ${env.BUILD_URL}"
                echo "JOB_NAME: ${env.JOB_NAME}"
            }
        }

        stage('Quality Checks') {
            parallel {
                stage('Lint') {
                    steps {
                        echo "Simulating Lint..."
                        sh 'echo "lint logs" > lint.log' 
                    }
                }
                stage('Test') {
                    steps {
                        echo "Simulating Tests..."
                        sh 'echo "test logs" > test.log'
                    }
                }
            }
        }

        stage('Deploy') {
            when {
                expression { params.SKIP_DEPLOY == false }
            }
            steps {
                echo "Deploying branch ${params.BRANCH_NAME}..."
            }
        }
    }

    post {
        always {
            echo "Pipeline finished"
        }
        success {
            echo "Success! Archiving logs..."
            // Архивируем только те файлы, которые ТОЧНО создались (логи)
            archiveArtifacts artifacts: '*.log', fingerprint: true
        }
        failure {
            echo "Failure! Cleaning workspace..."
            cleanWs()
        }
    }
}
