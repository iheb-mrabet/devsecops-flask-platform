pipeline {
    agent {
        docker {
            image 'python:3.11-slim'
        }
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest bandit pip-audit semgrep
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    mkdir -p .pytest-temp
                    python -m pytest -v --basetemp=.pytest-temp -p no:cacheprovider
                '''
            }
        }

        stage('Bandit SAST Scan') {
            steps {
                sh '''
                    python -m bandit -r app.py app -x tests,venv || true
                '''
            }
        }

        stage('Dependency Scan - pip-audit') {
            steps {
                sh '''
                    python -m pip_audit -r requirements.txt || true
                '''
            }
        }

        stage('Semgrep SAST Scan') {
            steps {
                sh '''
                    semgrep scan --config auto --exclude venv . || true
                '''
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished. Tests and security scans completed.'
        }
    }
}