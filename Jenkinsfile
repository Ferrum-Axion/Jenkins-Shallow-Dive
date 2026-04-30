pipeline{
    agent { label 'worker' }
    stages{
        stage('Branch_Info'){
            steps{
                echo "The branch name is ${env.BRANCH_NAME}"
                echo "Generic tag is  ${env.GIT_TAG_NAME}"
                echo "Generic tag is  ${env.GIT_TAG_NAME}"
            }
            steps{
                echo "The build id is ${env.BUILD_ID}"
            }
            steps{
                echo "The build URL is ${env.BUILD_URL}"
            }
        }
    }
} 