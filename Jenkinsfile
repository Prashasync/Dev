pipeline {
    agent any
    
    parameters {
        string(name: 'ECR_REPO_NAME', defaultValue: 'amazon-prime', description: 'Enter repository name')
        string(name: 'AWS_ACCOUNT_ID', defaultValue: '463470954735', description: 'Enter AWS Account ID')
    }
    
    environment {
        SCANNER_HOME = tool 'SonarQube Scanner'
        PYTHON = '/usr/bin/python3' // Reference the installed Python executable directly
        PIP = '/usr/bin/pip3'        // Reference pip3 directly
    }
    
    stages {
        stage('1. Git Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/Prashasync/Dev.git'
            }
        }
        /*
        stage('2. SonarQube Analysis') {
            steps {
                withSonarQubeEnv ('sonar-server') {
                    sh """
                    $SCANNER_HOME/bin/sonar-scanner \
                    -Dsonar.projectName=MVP_PrashaSync \
                    -Dsonar.projectKey=MVP_PrashaSync
                    """
                }
            }
        }
        
        stage('3. Quality Gate') {
            steps {
                waitForQualityGate abortPipeline: false, credentialsId: 'sonar-token'
            }
        }
        */
            stage('4. Install Python Dependencies') {
            steps {
                script {
                    echo 'Setting up Python virtual environment & installing dependencies'
                    sh """
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                    """
            }
        }
    }

        stage('5. Run Tests') {
            steps {
                script {
                    echo 'Checking if tests exist'
                    def test_files = sh(script: "find tests/ -type f -name '*.py' | wc -l", returnStdout: true).trim()
        
                    if (test_files.toInteger() > 0) {
                        echo 'Running Python tests'
                        sh """
                            . venv/bin/activate
                            pytest tests/
                        """
                    } else {
                        echo 'No tests found. Skipping pytest.'
                    }
                }
            }
        }


        
        stage('6. Trivy Scan') {
    steps {
        script {
            echo "Running Trivy vulnerability scan on Python dependencies"

            // Use the correct file pattern format
            sh '''
                trivy fs --scanners vuln --file-patterns "config:requirements\\.txt" --cache-dir /tmp/trivy-cache . > trivy.txt
                CRITICAL_COUNT=$(grep "CRITICAL" trivy.txt | wc -l || echo 0)
                if [ "$CRITICAL_COUNT" -ne 0 ]; then
                    echo "Critical vulnerabilities found! Failing pipeline."
                    exit 1
                fi
            '''
                }
            }
        }



        
        stage('7. Build Docker Image') {
            steps {
                sh "docker build -t ${params.ECR_REPO_NAME} ."
            }
        }
        
        stage('8. Create ECR repo') {
            steps {
                withCredentials([string(credentialsId: 'access-key', variable: 'AWS_ACCESS_KEY'), 
                                 string(credentialsId: 'secret-key', variable: 'AWS_SECRET_KEY')]) {
                    sh """
                    aws configure set aws_access_key_id $AWS_ACCESS_KEY
                    aws configure set aws_secret_access_key $AWS_SECRET_KEY
                    aws ecr describe-repositories --repository-names ${params.ECR_REPO_NAME} --region us-east-1 || \
                    aws ecr create-repository --repository-name ${params.ECR_REPO_NAME} --region us-east-1
                    """
                }
            }
        }
        
        stage('9. Login to ECR & tag image') {
            steps {
                withCredentials([string(credentialsId: 'access-key', variable: 'AWS_ACCESS_KEY'), 
                                 string(credentialsId: 'secret-key', variable: 'AWS_SECRET_KEY')]) {
                    sh """
                    aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${params.AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com
                    docker tag ${params.ECR_REPO_NAME} ${params.AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/${params.ECR_REPO_NAME}:${BUILD_NUMBER}
                    docker tag ${params.ECR_REPO_NAME} ${params.AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/${params.ECR_REPO_NAME}:latest
                    """
                }
            }
        }
        
        stage('10. Push image to ECR') {
            steps {
                withCredentials([string(credentialsId: 'access-key', variable: 'AWS_ACCESS_KEY'), 
                                 string(credentialsId: 'secret-key', variable: 'AWS_SECRET_KEY')]) {
                    sh """
                    docker push ${params.AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/${params.ECR_REPO_NAME}:${BUILD_NUMBER}
                    docker push ${params.AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/${params.ECR_REPO_NAME}:latest
                    """
                }
            }
        }
        
        stage('11. Cleanup Images') {
            steps {
                sh """
                docker rmi ${params.AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/${params.ECR_REPO_NAME}:${BUILD_NUMBER}
                docker rmi ${params.AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/${params.ECR_REPO_NAME}:latest
                docker images
                """
            }
        }
    }
}
