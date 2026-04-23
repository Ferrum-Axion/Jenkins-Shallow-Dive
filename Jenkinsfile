pipeline {
    agent { 
        label 'worker1 || worker2' 
    }

    stages {
        stage('Example Build') {
            steps {
                echo 'Building...'
                sh 'echo "binary content" > my-app-binary'
            }
        }

        stage('Pack the binary') {
            when {
                branch 'elenak-class-work'
            }
            steps {
                echo 'Compressing the binary...'
                sh 'tar -czvf binary.tar.gz my-app-binary'
            }
        }

        stage('Example Deploy') {
            when {
                branch 'elenak-class-work'
            }
            steps {
                echo 'Deploying...'
            }
        }
    }

    post {
        success {
            echo 'Archiving...'
            archiveArtifacts artifacts: 'binary.tar.gz', fingerprint: true
        }
    }
}
