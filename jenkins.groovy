pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                script {
                    sh """
                        # Ensure we are in a Git repository
                        if [ ! -d .git ]; then
                            echo "Not inside a git repository. Initializing..."
                            git init
                            git remote add origin git@github.com:Badafald/miraculin.git
                            git fetch origin
                            git checkout master
                        fi

                        # Reset any uncommitted changes and pull the latest code
                        git reset --hard
                        git pull origin master

                        # Ensure SSH key is used
                        git remote set-url origin git@github.com:Badafald/miraculin.git
                    """
                }
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
                                docker build -t badafald/miraculin-encrypt:${encryptionVersion} -f app/encryption_service/Dockerfile app/encryption_service
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
                                docker build -t badafald/miraculin-storage:${storageVersion} -f app/storage_service/Dockerfile app/storage_service
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
                                docker build -t badafald/miraculin-web:${webVersion} -f app/web_interface_service/Dockerfile app/web_interface_service
                            """
                        }
                    }
                }
            }
        }

        stage('Push images to DockerHUB') {
            parallel {
                stage('Push Encryption Image') {
                    steps {
                        script {
                            def encryptionVersion = env.ENCRYPTION_VERSION
                            docker.withRegistry('', 'a5072caf-57cf-4ad9-9cca-360a2148625d') {
                                sh "docker push badafald/miraculin-encrypt:${encryptionVersion}"
                            }
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
                            sh "docker rmi badafald/miraculin-web:${webVersion}"
                        }
                    }
                }
            }
        }

        stage('Update Helm values.yaml') {
            steps {
                script {
                    // Debugging: Check if values.yaml exists
                    sh "ls -lah helm"
                    sh "cat helm/values.yaml || echo 'values.yaml not found!'"

                    // Update values.yaml with new versions
                    sh """
                        sed -i 's|storage:[[:space:]]*version: v[0-9.]*|storage:\\n    version: ${env.STORAGE_VERSION}|' helm/values.yaml
                        sed -i 's|encryption:[[:space:]]*version: v[0-9.]*|encryption:\\n    version: ${env.ENCRYPTION_VERSION}|' helm/values.yaml
                        sed -i 's|web:[[:space:]]*version: v[0-9.]*|web:\\n    version: ${env.WEB_VERSION}|' helm/values.yaml
                    """

                    // Ensure file modification is detected
                    sh "touch helm/values.yaml"
                }
            }
        }

        stage('Commit and Push changes to GitHub') {
            steps {
                script {
                    sh "git checkout master"
                    sh "git pull origin master"

                    sh "git status"
                    sh "git diff helm/values.yaml || echo 'No changes detected'"

                    sh """
                        git config user.email "jenkins@miraculin.local"
                        git config user.name "Jenkins"

                        git add helm/values.yaml
                        git commit -m "Update Helm chart with new versions" || echo 'No changes to commit'
                        
                        # Push changes using SSH
                        GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no" git push origin master
                    """
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
