pipeline{
    agent {label 'deb'}
        stages {
            stage('Pre-Build') {
                steps {
                    sh '''
                    sudo apt-get update && sudo apt-get install -y  wget \
                                                                    curl \
                                                                    python3 \
                                                                    python3-pip \
                                                                    pipx \
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
                    steps {
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
                    }
                stage('Build'){
                    steps {
                    sh '''
                        chmod +x -R /home/jenkins/.local/pipx/venvs/pyinstaller
                        /home/jenkins/.local/pipx/venvs/pyinstaller -y  app.py
                    '''
                    }
                }
                stage('Archive'){
                            steps {
                    archiveArtifacts artifacts: 'dist', onlyIfSuccessful: true
                        }
                }
            }
        }
