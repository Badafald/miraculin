pipeline {
    agent any

    environment {
        DOCKER_REGISTRY = 'https://index.docker.io/v1/'
        CREDENTIALS_ID = 'a5072caf-57cf-4ad9-9cca-360a2148625d'
        GIT_REPO_SSH = 'git@github.com:Badafald/miraculin.git'
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    sh """
                        if [ ! -d .git ]; then
                            git init
                            git remote add origin ${env.GIT_REPO_SSH}
                            git fetch origin
                            git checkout master
                        fi
                        git reset --hard
                        git pull origin master
                        git remote set-url origin ${env.GIT_REPO_SSH}
                    """
                }
            }
        }

        stage('Setup') {
            steps {
                sh '''
                    mkdir -p reports
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r app/encryption_service/requirements.txt \
                                -r app/storage_service/requirements.txt \
                                -r app/web_interface_service/requirements.txt \
                                pytest pytest-xdist
                '''
            }
        }

        stage('Testing') {
            parallel {
                stage('Unit Tests - Encryption') {
                    steps {
                        withEnv(["PYTHONPATH=${env.WORKSPACE}/app/encryption_service"]) {
                            sh '. venv/bin/activate && pytest tests/unit/test_encryption.py --junitxml=reports/unit_encryption.xml'
                        }
                    }
                    post { always { junit 'reports/unit_encryption.xml' } }
                }

                stage('Unit Tests - Storage') {
                    steps {
                        withEnv(["PYTHONPATH=${env.WORKSPACE}/app/storage_service"]) {
                            sh '. venv/bin/activate && pytest tests/unit/test_storage.py --junitxml=reports/unit_storage.xml'
                        }
                    }
                    post { always { junit 'reports/unit_storage.xml' } }
                }

                stage('Integration Tests - Storage') {
                    steps {
                        withEnv(["PYTHONPATH=${env.WORKSPACE}/app/storage_service"]) {
                            sh '. venv/bin/activate && pytest tests/integration/test_storage_service.py --junitxml=reports/integration_storage.xml'
                        }
                    }
                    post { always { junit 'reports/integration_storage.xml' } }
                }

                stage('Integration Tests - Web Interface') {
                    steps {
                        withEnv(["PYTHONPATH=${env.WORKSPACE}/app/web_interface_service"]) {
                            sh '. venv/bin/activate && pytest tests/integration/test_web_interface.py --junitxml=reports/integration_webinterface.xml'
                        }
                    }
                    post { always { junit 'reports/integration_webinterface.xml' } }
                }
            }
        }

        stage('Build and Push Images with Check') {
            parallel {
                stage('Encryption Service') {
                    steps {
                        script {
                            def ENC_VER = readFile('app/encryption_service/version').trim()
                            def ENC_IMAGE = "badafald/miraculin-encrypt:${ENC_VER}"
                            def encExists = sh(script: "set +e; docker manifest inspect ${ENC_IMAGE} > /dev/null 2>&1; echo \$?", returnStdout: true).trim()
                            if (encExists != '0') {
                                sh "docker build -t ${ENC_IMAGE} -f app/encryption_service/Dockerfile app/encryption_service"
                                docker.withRegistry(env.DOCKER_REGISTRY, env.CREDENTIALS_ID) {
                                    sh "docker push ${ENC_IMAGE}"
                                }
                                sh "docker rmi ${ENC_IMAGE}"
                            } else {
                                echo "Encryption image ${ENC_IMAGE} already exists — skipping build."
                            }
                        }
                    }
                }

                stage('Storage Service') {
                    steps {
                        script {
                            def STOR_VER = readFile('app/storage_service/version').trim()
                            def STOR_IMAGE = "badafald/miraculin-storage:${STOR_VER}"
                            def encExists = sh(script: "docker manifest inspect ${ENC_IMAGE} > /dev/null 2>&1 && echo 0 || echo 1", returnStdout: true).trim()
                            if (storExists != '0') {
                                sh "docker build -t ${STOR_IMAGE} -f app/storage_service/Dockerfile app/storage_service"
                                docker.withRegistry(env.DOCKER_REGISTRY, env.CREDENTIALS_ID) {
                                    sh "docker push ${STOR_IMAGE}"
                                }
                                sh "docker rmi ${STOR_IMAGE}"
                            } else {
                                echo "Storage image ${STOR_IMAGE} already exists — skipping build."
                            }
                        }
                    }
                }

                stage('Web Interface Service') {
                    steps {
                        script {
                            def WEB_VER = readFile('app/web_interface_service/version').trim()
                            def WEB_IMAGE = "badafald/miraculin-web:${WEB_VER}"
                            def webExists = sh(script: "set +e; docker manifest inspect ${WEB_IMAGE} > /dev/null 2>&1; echo \$?", returnStdout: true).trim()
                            if (webExists != '0') {
                                sh "docker build -t ${WEB_IMAGE} -f app/web_interface_service/Dockerfile app/web_interface_service"
                                docker.withRegistry(env.DOCKER_REGISTRY, env.CREDENTIALS_ID) {
                                    sh "docker push ${WEB_IMAGE}"
                                }
                                sh "docker rmi ${WEB_IMAGE}"
                            } else {
                                echo "Web interface image ${WEB_IMAGE} already exists — skipping build."
                            }
                        }
                    }
                }
            }
        }

        stage('Update Helm values.yaml') {
            steps {
                script {
                    def ENC_VER = readFile('app/encryption_service/version').trim()
                    def STOR_VER = readFile('app/storage_service/version').trim()
                    def WEB_VER = readFile('app/web_interface_service/version').trim()

                    sh """
                        sed -i 's/version:.*/version: ${STOR_VER}/' helm/values-storage.yaml
                        sed -i 's/version:.*/version: ${ENC_VER}/' helm/values-encryption.yaml
                        sed -i 's/version:.*/version: ${WEB_VER}/' helm/values-web.yaml
                    """
                }
            }
        }

        stage('Commit and Push changes to GitHub') {
            steps {
                script {
                    sh "git checkout master"
                    sh "git pull origin master"

                    sh """
                        git config user.email "jenkins@miraculin.local"
                        git config user.name "Jenkins"
                        git add helm/values-*.yaml
                        git commit -m "Update Helm chart with new versions" || echo 'No changes to commit'
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
