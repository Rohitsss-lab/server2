pipeline {
    agent any
    tools {
        nodejs 'NodeJS-20'
    }
    parameters {
        string(name: 'BUMP_TYPE', defaultValue: 'patch', description: 'Version bump type')
    }
    environment {
        GIT_REPO_URL = 'https://github.com/Rohitsss-lab/ver2.git'
    }
    stages {
        stage('Clean Workspace') {
            steps {
                cleanWs()
            }
        }
        stage('Checkout') {
            steps {
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
        stage('Install Dependencies') {
            steps {
                bat 'npm install'
            }
        }
        stage('Run Tests') {
            steps {
                bat 'npm test'
            }
        }
        stage('Bump Version') {
            steps {
                withEnv(["BUMP_TYPE=${params.BUMP_TYPE}"]) {
                    bat '"C:\\Program Files\\Python313\\python.exe" bump_version.py'
                }
            }
        }
        stage('Commit and Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'github-token',
                    usernameVariable: 'GIT_USER',
                    passwordVariable: 'GIT_TOKEN'
                )]) {
                    script {
                        def newVersion = readFile('NEW_VERSION.txt').trim()
                        env.NEW_VERSION = newVersion
                    }
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
        stage('Notify vertotal') {
            steps {
                script {
                    def newVersion = readFile('NEW_VERSION.txt').trim()
                    echo "============================================"
                    echo "NEW VERSION FILE CONTAINS: ${newVersion}"
                    echo "JOB BEING CALLED: vertotal-pipeline"
                    echo "REPO_NAME being sent: ver1"
                    echo "REPO_VERSION being sent: ${newVersion}"
                    echo "============================================"
                    build job: 'vertotal-pipeline',
                          wait: true,
                          parameters: [
                              string(name: 'REPO_NAME',    value: 'ver2'),
                              string(name: 'REPO_VERSION', value: newVersion),
                              string(name: 'BUMP_TYPE',    value: 'patch')
                          ]
                }
            }
        }
    }
    post {
        success { echo "ver1 pipeline completed successfully" }
        failure { echo "ver1 pipeline FAILED" }
    }
}
