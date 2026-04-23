pipeline{
    agent { label 'deb' }
    stages{
        stage('Prebuild'){
            steps{
                sh '''
                apt-get update 
                apt-get install -y python3 python3-pip python3-flask pylint pipx curl wget git
                pipx install pyinstaller
                '''
                // Installing projetc dependencies 
            }
        }
        stage('Clone'){
            steps{
                sh '''
                if [ -e jenkins-examples ];then
                    rm -rf jenkins-examples
                fi
                git clone https://gitlab.com/vaiolabs-io/jenkins-examples.git
                '''
            }
        }
        stage('Lint'){
            steps{
                sh 'pylint --disable=missing-docstring,invalid-name .'
            }
        }
        stage('Build'){
            steps{
                sh '''
                PATH="$PATH:/root/.local/bin"
                pyinstaller -y jenkins-examples/app.py
                '''
            }
        }
        stage('Test'){
            steps{
                echo 'Testing app..'
            }
        }
        stage('Archive'){
            steps{
                sh 'tar -czvf app.tar.gz dist/app'
                echo 'Archiving the artifact'
                archiveArtifacts artifacts: 'app.tar.gz', followSymlinks: false
            }
        }
        post {
            success { archiveArtifacts artifacts: 'app.tar.gz', followSymlinks: false }
            unsuccess { cleanWs() }
        }
    }
}
