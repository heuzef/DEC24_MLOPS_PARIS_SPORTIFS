pipeline {
    agent any

    environment {
      REPO_PATH = "/home/parivision/DEC24_MLOPS_PARIS_SPORTIFS"
      VENV_PATH = "${REPO_PATH}/.venv/bin/activate"
      }

    stages {
        stage("Get data") {
          steps {
                sh """#!/bin/bash
                cd ${REPO_PATH}
                source ${VENV_PATH}
                python3 src/get_data.py
                """
          }
        }
        stage("Create Dataset") {
          steps {
                sh """#!/bin/bash
                cd ${REPO_PATH}
                source ${VENV_PATH}
                python3 src/process_data.py
                """
          }
        }
        stage("Train Model") {
          steps {
                sh """#!/bin/bash
                cd ${REPO_PATH}
                source ${VENV_PATH}
                python3 src/train_model.py
                """
          }
        }
        stage("Deploy Model") {
          steps {
                sh """#!/bin/bash
                cd ${REPO_PATH}
                source ${VENV_PATH}
                sh src/deploy_model.sh
                """
          }
        }
    }
}