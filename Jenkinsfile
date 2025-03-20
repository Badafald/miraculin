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
                    // Use the correct variable name and check
                    def storExists = sh(script: "set +e; docker manifest inspect ${STOR_IMAGE} > /dev/null 2>&1; echo \$?", returnStdout: true).trim()
                    
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
