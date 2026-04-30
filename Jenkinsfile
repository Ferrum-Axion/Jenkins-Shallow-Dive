
pipeline{
    parameters{
        string(name: 'sleep_time', defaultValue: '2', description:'time to sleep')
        choice(name: 'Agent_name', choices: ['deb','debs','fedora', 'win'], description:'Pick a agent to run on ')
    }
    agent any

    stages{
        stage('Pre-Build'){
                agent { docker { image 'python:3.11' } }
            steps{
        
                echo 'Checking pre-requisites'
                echo 'TESTING WHATEVER'
                sleep "${params.sleep_time}"
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
                      agent { docker { image 'python:3.11' } }

            steps{
                echo 'Static code analysis check'
                sleep "${params.sleep_time}"
                sh '''
	
                    pylint --disable=missing-docstring,invalid-name app.py 
                '''
	    } //error with artifact
	}
        stage('Build'){
                agent { docker { image 'python:3.11' } }

            steps{
                echo 'Building the Project'
                sleep "${params.sleep_time}"
                sh '''
                    python3 app.py &
		            chmod 777 -R  /home/jenkins/.local/bin/pyinstaller
		            /home/jenkins/.local/bin/pyinstaller -y  app.py
                '''
            }// error with pyinstaller
        }
        stage('Test'){
                            agent { docker { image 'python:3.11' } }

            steps{
                echo 'Testing'
                sleep "${params.sleep_time}"
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
}
 	   post {
        	unsuccessful{
            	cleanWs cleanWhenSuccess: false
       		 	}
        	success{
            		archiveArtifacts artifacts: 'dist/', followSymlinks: false, onlyIfSuccessful: true      
        		}
    		}

    	}


