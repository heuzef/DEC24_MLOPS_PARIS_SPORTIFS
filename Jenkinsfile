pipeline {
    agent any

    environment {
      REPO_PATH = "/home/parivision/DEC24_MLOPS_PARIS_SPORTIFS"
      VENV_PATH = "${REPO_PATH}/.venv/bin/activate"
      }

    stages {
        stage("Récupération des données") {
          steps {
                sh """#!/bin/bash
                cd ${REPO_PATH}
                source ${VENV_PATH}
                python3 src/get_data.py 100
                """
          }
        }
        stage("Pré-traitement des données") {
          steps {
                sh """#!/bin/bash
                cd ${REPO_PATH}
                source ${VENV_PATH}
                python3 src/process_data.py
                """
          }
        }
        stage("Generate Drift Monitoring Report") {
          steps {
                sh """#!/bin/bash
                cd ${REPO_PATH}
                source ${VENV_PATH}
                # python3 monitoring/evidently/main.py
                echo "Generation du rapport de dérive des données"
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
        stage("MLFlow Champion") {
          steps {
                sh """#!/bin/bash
                cd ${REPO_PATH}
                source ${VENV_PATH}
                python3 src/mlflow_champion.py
                """
          }
        }
        stage("Deploy Model") {
          steps {
                sh """#!/bin/bash
                cd ${REPO_PATH}
                sh src/deploy_model.sh
                """
          }
        }
        stage("Deploy App") {
          steps {
                sh """#!/bin/bash
                cd ${REPO_PATH}
                sh src/deploy_app.sh
                """
          }
        }
    }
}