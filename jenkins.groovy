pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scmGit(
                    branches: [[name: '*/master']],
                    extensions: [],
                    userRemoteConfigs: [[url: 'https://github.com/Badafald/miraculin.git']]
                )
            }
        }
        stage('Setup') {
            steps {
                echo "Creating reports directory..."
                sh 'mkdir -p reports'
                echo "Creating virtual environment..."
                sh 'python3 -m venv venv'
                echo "Activating virtual environment and installing dependencies..."
                sh '''
                    . venv/bin/activate
                    pip install -r app/encryption_service/requirements.txt
                    pip install -r app/storage_service/requirements.txt
                    pip install -r app/web_interface_service/requirements.txt
                    pip install pytest pytest-xdist
                '''
            }
        }

        stage('Testing') {
            parallel {
                stage('Unit Tests - Encryption') {
                    steps {
                        withEnv(["PYTHONPATH=${env.WORKSPACE}/app/encryption_service"]) {
                            sh '. venv/bin/activate && venv/bin/pytest tests/unit/test_encryption.py --junitxml=reports/unit_encryption.xml'
                        }
                    }
                    post {
                        always {
                            junit 'reports/unit_encryption.xml'
                        }
                    }
                }
                stage('Unit Tests - Storage') {
                    steps {
                        withEnv(["PYTHONPATH=${env.WORKSPACE}/app/storage_service"]) {
                            sh '. venv/bin/activate && venv/bin/pytest tests/unit/test_storage.py --junitxml=reports/unit_storage.xml'
                        }
                    }
                    post {
                        always {
                            junit 'reports/unit_storage.xml'
                        }
                    }
                }
                stage('Integration Tests - Storage') {
                    steps {
                        withEnv(["PYTHONPATH=${env.WORKSPACE}/app/storage_service"]) {
                            sh '. venv/bin/activate && venv/bin/pytest tests/integration/test_storage_service.py --junitxml=reports/integration_storage.xml'
                        }
                    }
                    post {
                        always {
                            junit 'reports/integration_storage.xml'
                        }
                    }
                }
                stage('Integration Tests - Web Interface') {
                    steps {
                        withEnv(["PYTHONPATH=${env.WORKSPACE}/app/web_interface_service"]) {
                            sh '. venv/bin/activate && venv/bin/pytest tests/integration/test_web_interface.py --junitxml=reports/integration_webinterface.xml'
                        }
                    }
                    post {
                        always {
                            junit 'reports/integration_webinterface.xml'
                        }
                    }
                }
            }
        }
    stage('Building service images') {
            parallel { 
                stage('Build Encryption Image') {
                    steps {
                        script {
                            def encryptionVersion = readFile('app/encryption_service/version').trim()
                            env.ENCRYPTION_VERSION = encryptionVersion
                            echo "Encryption Service Version: ${encryptionVersion}"
                            sh """
                                docker build \
                                -t badafald/miraculin-encrypt:${encryptionVersion} \
                                -f app/encryption_service/Dockerfile \
                                app/encryption_service
                            """
                        }
                    }
                }

                stage('Build Storage Image') {
                    steps {
                        script {
                            def storageVersion = readFile('app/storage_service/version').trim()
                            env.STORAGE_VERSION = storageVersion
                            echo "Storage Service Version: ${storageVersion}"
                            sh """
                                docker build \
                                -t badafald/miraculin-storage:${storageVersion} \
                                -f app/storage_service/Dockerfile \
                                app/storage_service
                            """
                        }
                    }
                }

                stage('Build Web Interface Image') {
                    steps {
                        script {
                            def webVersion = readFile('app/web_interface_service/version').trim()
                            env.WEB_VERSION = webVersion
                            echo "Web Interface Service Version: ${webVersion}"
                            sh """
                                docker build \
                                -t badafald/miraculin-web:${webVersion} \
                                -f app/web_interface_service/Dockerfile \
                                app/web_interface_service
                            """
                        }
                    }
                }
            }
        }

    stage ('Push images to DockerHUB') { 
        parallel { 
            stage('Push Encryption Image') {
                    steps {
                        script {
                            def encryptionVersion = env.ENCRYPTION_VERSION
                            docker.withRegistry('', 'a5072caf-57cf-4ad9-9cca-360a2148625d') {
                                sh "docker push badafald/miraculin-encrypt:${encryptionVersion}"
                            }
                            // Remove the local image to free up storage
                            sh "docker rmi badafald/miraculin-encrypt:${encryptionVersion}"
                        }
                    }
                }

                stage('Push Storage Image') {
                    steps {
                        script {
                            def storageVersion = env.STORAGE_VERSION
                            docker.withRegistry('https://index.docker.io/v1/', 'a5072caf-57cf-4ad9-9cca-360a2148625d') {
                                sh "docker push badafald/miraculin-storage:${storageVersion}"
                            }
                            // Remove the local image to free up storage
                            sh "docker rmi badafald/miraculin-storage:${storageVersion}"
                        }
                    }
                }

                stage('Push Web Interface Image') {
                    steps {
                        script {
                            def webVersion = env.WEB_VERSION
                            docker.withRegistry('https://index.docker.io/v1/', 'a5072caf-57cf-4ad9-9cca-360a2148625d') {
                                sh "docker push badafald/miraculin-web:${webVersion}"
                            }
                            // Remove the local image to free up storage
                            sh "docker rmi badafald/miraculin-web:${webVersion}"
                        }
                    }
                }
            }
        }
    }



    
    post {
        always {
            archiveArtifacts artifacts: 'reports/*.xml', allowEmptyArchive: true
        }
    }
}
