
pipeline{
    agent {label 'deb'}

    stages{
        stage('Pre-Build'){
            steps{
                echo 'Checking pre-requisites'
                sleep 2
                sh'''
                    . /etc/os-release
                    if [ $ID == 'debian' ];then
                        sudo apt-get update
                        sudo apt-get install -y wget curl python3 python3-pip python3-pep8 python3-flask pipenv pylint pipx
		                pipx install pyinstaller
                    fi
                    if [ $ID == 'rocky' ];then
                        sudo dnf install -y wget curl python3 python3-pip python3-pytest-flake8 python3-flask micropipenv pylint pipx --skip-broken
                    fi
                '''
            }
        }
        stage('Linter'){
            steps{
                echo 'Static code analysis check'
                sleep 2
                sh '''
	
                    pylint --disable=missing-docstring,invalid-name app.py 
                '''
            } //error with artifact
        }
        stage('Build'){
            steps{
                echo 'Building the Project'
                sleep 2
                sh '''
                    python3 app.py &
		            chmod 777 -R  /home/jenkins/.local/bin/pyinstaller
		            /home/jenkins/.local/bin/pyinstaller  app.py
                '''
            }// error with pyinstaller
        }
        stage('Test'){
            steps{
                echo 'Testing'
                sh'''
                    if curl localhost:8080 &> /dev/null;then
                        echo 'post test: success'
                    else
                        echo 'post test: fail'
                        exit 1
                    fi
                    if curl localhost:8080/jenkins &> /dev/null;then
                        echo 'post test with variable: success'
                    else
                        echo 'post test with variable: fail'
                        exit 1
                    fi
                '''
            }
        }
 	   post {
        	unsuccessful{
            	cleanWs cleanWhenSuccess: false
       		 	}
        	successful{
            		archiveArtifacts artifacts: '/home/jenkins/workspace/flask/dist/app', followSymlinks: false, onlyIfSuccessful: true      
        		}
    		}

    	}
}

