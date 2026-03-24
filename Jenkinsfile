pipeline {
    agent any
    tools {
        nodejs 'NodeJS-20'
    }
    parameters {
        string(name: 'BUMP_TYPE',           defaultValue: 'patch', description: 'Version bump type')
        string(name: 'DEPLOY_TAG',          defaultValue: '',      description: 'Tag to deploy')
        string(name: 'TRIGGERED_BY_DEPLOY', defaultValue: 'false', description: 'Set true when called from vertot')
    }
    environment {
        GIT_REPO_URL = 'https://github.com/Rohitsss-lab/server2.git'
        SERVER_IP    = '192.168.3.178'
        DEPLOY_PATH  = '/root/ver2'
    }
    stages {
        stage('Clean Workspace') {
            steps { cleanWs() }
        }
        stage('Checkout') {
            steps {
                script {
                    if (params.DEPLOY_TAG?.trim()) {
                        checkout([
                            $class: 'GitSCM',
                            branches: [[name: "v${params.DEPLOY_TAG}"]],
                            userRemoteConfigs: [[
                                url: "${env.GIT_REPO_URL}",
                                credentialsId: 'github-token'
                            ]],
                            extensions: [[$class: 'CloneOption', noTags: false]]
                        ])
                    } else {
                        checkout([
                            $class: 'GitSCM',
                            branches: [[name: '*/main']],
                            userRemoteConfigs: [[
                                url: "${env.GIT_REPO_URL}",
                                credentialsId: 'github-token'
                            ]]
                        ])
                    }
                }
            }
        }
        stage('Install Dependencies') {
            steps { bat 'npm install' }
        }
        stage('Run Tests') {
            when {
                expression { return params.DEPLOY_TAG == null || params.DEPLOY_TAG.trim() == '' }
            }
            steps { bat 'npm test' }
        }
        stage('Bump Version') {
            when {
                expression { return params.DEPLOY_TAG == null || params.DEPLOY_TAG.trim() == '' }
            }
            steps {
                withEnv(["BUMP_TYPE=${params.BUMP_TYPE}"]) {
                    bat '"C:\\Program Files\\Python313\\python.exe" bump_version.py'
                }
                script {
                    env.NEW_VERSION = readFile('NEW_VERSION.txt')
                                        .replaceAll('[^0-9.]', '').trim()
                    echo "BUMPED VERSION = ${env.NEW_VERSION}"
                }
            }
        }
        stage('Commit and Push') {
            when {
                expression { return params.DEPLOY_TAG == null || params.DEPLOY_TAG.trim() == '' }
            }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'github-token',
                    usernameVariable: 'GIT_USER',
                    passwordVariable: 'GIT_TOKEN'
                )]) {
                    bat '''
                        git config user.email "jenkins@ci.com"
                        git config user.name "Jenkins"
                        git checkout -b release/v%NEW_VERSION%
                        git add versions.json package.json
                        git commit -m "chore: bump version to v%NEW_VERSION%"
                        git remote set-url origin https://%GIT_USER%:%GIT_TOKEN%@github.com/Rohitsss-lab/server2.git
                        git push origin release/v%NEW_VERSION%
                        git checkout main
                        git merge release/v%NEW_VERSION%
                        git push origin main
                        git tag v%NEW_VERSION% || echo "Tag already exists"
                        git push origin v%NEW_VERSION% || echo "Tag already pushed"
                    '''
                }
            }
        }
        stage('Deploy to Server') {
            when {
                expression { return params.DEPLOY_TAG != null && params.DEPLOY_TAG.trim() != '' }
            }
            steps {
                script {
                    def deployVersion = params.DEPLOY_TAG.trim()
                    echo "==========================================="
                    echo "Deploying server2 v${deployVersion} to ${env.SERVER_IP}"
                    echo "==========================================="
                    withCredentials([file(credentialsId: 'deploy-ssh-key-file', variable: 'SSH_KEY')]) {
                        bat """
                            copy "%SSH_KEY%" "%TEMP%\\deploy_key"
                            ssh -i "%TEMP%\\deploy_key" -o StrictHostKeyChecking=no root@${env.SERVER_IP} "cd ${env.DEPLOY_PATH} && git fetch --tags && git checkout tags/v${deployVersion} -f && npm install --production && pm2 restart ver2 || pm2 start src/index.js --name ver2 && pm2 save"
                            del "%TEMP%\\deploy_key"
                        """
                    }
                    echo "server2 v${deployVersion} is LIVE on server"
                }
            }
        }
        stage('Notify vertot') {
            when {
                allOf {
                    expression { return params.DEPLOY_TAG == null || params.DEPLOY_TAG.trim() == '' }
                    expression { return params.TRIGGERED_BY_DEPLOY == 'false' }
                }
            }
            steps {
                script {
                    def sendVersion = readFile('NEW_VERSION.txt')
                                        .replaceAll('[^0-9.]', '').trim()
                    echo "Sending server2 version ${sendVersion} to vertot"
                    build job: 'vertot',
                          wait: true,
                          parameters: [
                              string(name: 'REPO_NAME',      value: 'server2'),
                              string(name: 'REPO_VERSION',   value: sendVersion),
                              string(name: 'BUMP_TYPE',      value: 'patch'),
                              string(name: 'DEPLOY_VERSION', value: '')
                          ]
                }
            }
        }
    }
    post {
        success { echo "server2 pipeline completed successfully" }
        failure { echo "server2 pipeline FAILED" }
    }
}
