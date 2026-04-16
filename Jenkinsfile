pipeline{
    agent {label 'workers'}
        stages {
            stage('Pre-Build') {
                steps {
                    sh '''
                    sudo apt-get update && sudo apt-get install -y  wget \
                                                                    curl \
                                                                    python3 \
                                                                    python3-pip \
                                                                    pipx
                                                                    python3-pep8 \
                                                                    python3-flask \
                                                                    pipenv  \
                                                                    pylint  \
                                                                    python-poetry
                    pipx install pyinstaller
                    '''
                    }
                }
                stage('Linter') {
                    steps {
                            sh '''
                            pylint   --disable=missing-docstring,invalid-name .
                            '''
                        }
                    }
                stage('Test') {
                        sh'''
                            python3 ./app.py
                            if curl localhost:8080 > /dev/null 2>&1
                                then
                                        echo "Test SUCCESSFUL"
                                        sleep 2
                            else
                                        echo "Test FAILED"
                                        sleep 2
                                        exit 1
                            fi
                        '''
                        }
                stage('Build'){
                    sh '''
                        chmod +x -R /home/jenkins/.local/pipx/venvs/pyinstaller
                        /home/jenkins/.local/pipx/venvs/pyinstaller -y  app.py
                    '''
                }
                stage('Archive'){
                    archiveArtifacts artifacts: 'dist', onlySuccessful: true
                }
                    }
            }
}