pipeline {
    agent {
        docker {
            image 'python:3.12' // Specify the Docker image to use
            args '-v /var/run/docker.sock:/var/run/docker.sock' // Allow Docker commands within the container
        }
    }

    stages {
        stage('Checkout') {
            steps {
                // Using git clone to fetch the repository
                sh 'rm -rf RubHew-MobileAppProject' // Clean up any previous clones
                sh 'git clone https://github.com/aempee1/RubHew-MobileAppProject.git'
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                dir('RubHew-MobileAppProject') {
                    sh '''
                        python -m venv venv
                        . venv/bin/activate
                        pip install poetry
                        poetry install
                    '''
                }
            }
        } 
        
        stage('Create Env file') {
            steps {
                dir('RubHew-MobileAppProject') {
                    sh '''
                        echo "SQLDB_URL=sqlite+aiosqlite:///./test-data/test-sqlalchemy.db" > .testing.env
                        echo "Server_URL=http://localhost:8000" >> .testing.env
                    '''
                }
            }
        }
        
        stage('Test SonarScanner') {
            steps {
                dir('RubHew-MobileAppProject') {
                    sh '''
                        export PATH=/opt/java/openjdk/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/var/jenkins_home/sonar-scanner-6.2.1.4610-linux-x64/bin
                        sonar-scanner \
                          -Dsonar.projectKey=test_fastapi \
                          -Dsonar.sources=. \
                          -Dsonar.host.url=http://localhost:9000 \
                          -Dsonar.token=sqp_c24993b73bf2bf7dbcd29b329be407b1025e2ba2
                    '''
                }
            }
        }
        
        stage('PyTest') {
            steps {
                dir('RubHew-MobileAppProject') {
                    sh '''
                        . venv/bin/activate
                        export $(cat .testing.env | xargs)
                        poetry run pytest -v
                    '''
                }
            }
        }
    }
}
