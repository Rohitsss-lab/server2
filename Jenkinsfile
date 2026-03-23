pipeline {
    agent any
    tools {
        nodejs 'NodeJS-20'
    }
    parameters {
        string(name: 'BUMP_TYPE',           defaultValue: 'patch', description: 'Version bump type')
        string(name: 'DEPLOY_TAG',          defaultValue: '',      description: 'Tag to deploy — leave blank for normal build')
        string(name: 'TRIGGERED_BY_DEPLOY', defaultValue: 'false', description: 'Set true when called from vertot deploy')
    }
    environment {
        GIT_REPO_URL = 'https://github.com/Rohitsss-lab/ver2.git'
        IS_DEPLOY    = "${params.DEPLOY_TAG?.trim() ? 'true' : 'false'}"
    }
    stages {
        stage('Clean Workspace') {
            steps {
                cleanWs()
            }
        }
        stage('Checkout') {
            steps {
                script {
                    if (params.DEPLOY_TAG?.trim()) {
                        checkout([
                            $class: 'GitSCM',
                            branches: [[name: "refs/tags/v${params.DEPLOY_TAG}"]],
                            userRemoteConfigs: [[
                                url: "${env.GIT_REPO_URL}",
                                credentialsId: 'github-token'
                            ]]
                        ])
                        echo "Checked out ver2 at tag v${params.DEPLOY_TAG}"
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
            steps {
                bat 'npm install'
            }
        }
        stage('Run Tests') {
            when {
                environment name: 'IS_DEPLOY', value: 'false'
            }
            steps {
                bat 'npm test'
            }
        }
        stage('Bump Version') {
            when {
                environment name: 'IS_DEPLOY', value: 'false'
            }
            steps {
                withEnv(["BUMP_TYPE=${params.BUMP_TYPE}"]) {
                    bat '"C:\\Program Files\\Python313\\python.exe" bump_version.py'
                }
                script {
                    // Read and store version immediately after bump
                    def newVersion = readFile('NEW_VERSION.txt').trim()
                    env.NEW_VERSION = newVersion
                    echo "New version is: ${env.NEW_VERSION}"
                }
            }
        }
        stage('Commit and Push') {
            when {
                environment name: 'IS_DEPLOY', value: 'false'
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
                        git remote set-url origin https://%GIT_USER%:%GIT_TOKEN%@github.com/Rohitsss-lab/ver2.git
                        git push origin release/v%NEW_VERSION%
                        git checkout main
                        git merge release/v%NEW_VERSION%
                        git push origin main
                        git tag v%NEW_VERSION%
                        git push origin v%NEW_VERSION%
                    '''
                }
            }
        }
        stage('Deploy') {
            when {
                environment name: 'IS_DEPLOY', value: 'true'
            }
            steps {
                echo "==========================================="
                echo "DEPLOYING ver2 at tag ${params.DEPLOY_TAG}"
                echo "==========================================="
                bat 'npm install'
                echo "ver2 v${params.DEPLOY_TAG} deployed on port 3002"
            }
        }
        stage('Notify vertot') {
            when {
                allOf {
                    environment name: 'IS_DEPLOY', value: 'false'
                    expression { return params.TRIGGERED_BY_DEPLOY == 'false' }
                }
            }
            steps {
                script {
                    echo "==========================================="
                    echo "Notifying vertot with version: ${env.NEW_VERSION}"
                    echo "==========================================="
                    build job: 'vertot',
                          wait: true,
                          parameters: [
                              string(name: 'REPO_NAME',    value: 'ver2'),
                              string(name: 'REPO_VERSION', value: env.NEW_VERSION),
                              string(name: 'BUMP_TYPE',    value: 'patch'),
                              string(name: 'DEPLOY_VERSION', value: '')
                          ]
                }
            }
        }
    }
    post {
        success { echo "ver2 pipeline completed successfully" }
        failure { echo "ver2 pipeline FAILED" }
    }
}
