
pipeline{
    parameters{
        string(name: 'sleep_time', defaultValue: '2', description:'time to sleep')
        choice(name: 'Agent_name', choices: ['deb', 'win'], description:'Pick a agent to run on ')
        string(name: 'BRANCH_NAME', defaultValue: 'main', description:'Branch to build')
		booleanParam(name: 'SKIP_DEPLOY', defaultvalue: false, description: 'Skip the deploy stage')
	}
    agent { label "${params.Agent_name}"}

    stages{
        stage('Pre-Build'){
            steps{
                echo 'Checking pre-requisites'
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

		stage('Info') {
			steps {
				echo "Build ID : ${env.BUILD_ID}"
				echo "Build URL : ${env.BUILD_URL}"
				echo "Job Name : ${env.JOB_NAME}"
				echo "Branch : ${params.BRANCH_NAME}"
		}
	}
		
		stage('Validate') {
			failFast true
				parallel {
					stage('Lint') {
						steps {
							echo 'Running linter...'
							sh 'echo lint-output > lint.log'
						}
					}
					stage('Test') {
						steps {
							echo 'Running tests...'
							sh 'echo test-output > test.log'
						}
					}
			}
		}

		post {
			always {
				echo 'Pipeline finished.'
			}
			success {
				archiveArtifacts artifacts: '*.log', allowEmptyArchive: true
			}
			failure {
				cleanWs()
			}
		}
	}

